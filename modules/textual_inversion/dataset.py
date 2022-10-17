import os
import numpy as np
import PIL
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

import random
import tqdm
from modules import devices, shared
import re

re_numbers_at_start = re.compile(r"^[-\d]+\s*")


class DatasetEntry:
    def __init__(self, filename=None, latent=None, filename_text=None, timg=None):
        self.filename = filename
        self.latent = latent
        self.filename_text = filename_text
        self.timg = timg
        self.cond = None
        self.cond_text = None


class PersonalizedBase(Dataset):
    def __init__(self, data_root, width, height, repeats, flip_p=0.5, placeholder_token="*", model=None, device=None, template_file=None, include_cond=False, batch_size=1):
        re_word = re.compile(shared.opts.dataset_filename_word_regex) if len(shared.opts.dataset_filename_word_regex) > 0 else None

        self.placeholder_token = placeholder_token

        self.batch_size = batch_size
        self.width = width
        self.height = height
        self.flip = transforms.RandomHorizontalFlip(p=flip_p)

        self.dataset = []

        with open(template_file, "r") as file:
            lines = [x.strip() for x in file.readlines()]

        self.lines = lines

        assert data_root, 'dataset directory not specified'

        # rasize and crop, not change the image ratio
        TR = transforms.Compose([
            transforms.Resize(min(self.width, self.height), interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.CenterCrop(min(self.width, self.height)),
            transforms.ToTensor()
        ])

        cond_model = shared.sd_model.cond_stage_model

        self.image_paths = [os.path.join(data_root, file_path) for file_path in os.listdir(data_root)]
        print("Preparing dataset...")
        for path in tqdm.tqdm(self.image_paths):
            try:
                image = Image.open(path).convert('RGB')
            except Exception:
                continue

            text_filename = os.path.splitext(path)[0] + ".txt"
            filename = os.path.basename(path)

            if os.path.exists(text_filename):
                with open(text_filename, "r", encoding="utf8") as file:
                    filename_text = file.read()
            else:
                filename_text = os.path.splitext(filename)[0]
                filename_text = re.sub(re_numbers_at_start, '', filename_text)
                if re_word:
                    tokens = re_word.findall(filename_text)
                    filename_text = (shared.opts.dataset_filename_join_string or "").join(tokens)

            torchdata = (TR(image) * 2. - 1.).to(device=device, dtype=torch.float32)

            timg = torchdata.unsqueeze(dim=0)
            init_latent = model.get_first_stage_encoding(model.encode_first_stage(timg)).squeeze()
            init_latent = init_latent.to(devices.cpu)

            entry = DatasetEntry(filename=path, filename_text=filename_text, latent=init_latent, timg=timg)

            if include_cond:
                entry.cond_text = self.create_text(filename_text)
                entry.cond = cond_model([entry.cond_text]).to(devices.cpu).squeeze(0)

            self.dataset.append(entry)

        assert len(self.dataset) >= 1, "No images have been found in the dataset." # support one-shot training
        self.length = len(self.dataset) * repeats // batch_size

        self.initial_indexes = np.arange(len(self.dataset))
        self.indexes = None
        self.shuffle()

    def shuffle(self):
        self.indexes = self.initial_indexes[torch.randperm(self.initial_indexes.shape[0])] if len(self.dataset)>1 else self.initial_indexes

    def create_text(self, filename_text):
        text = random.choice(self.lines)
        text = text.replace("[name]", self.placeholder_token)
        text = text.replace("[filewords]", filename_text)
        return text

    def __len__(self):
        return self.length

    def __getitem__(self, i):
        res = []

        for j in range(self.batch_size):
            position = i * self.batch_size + j
            if position % len(self.indexes) == 0:
                self.shuffle()

            index = self.indexes[position % len(self.indexes)]
            entry = self.dataset[index]

            if entry.cond is None:
                entry.cond_text = self.create_text(entry.filename_text)

            res.append(entry)

        return res

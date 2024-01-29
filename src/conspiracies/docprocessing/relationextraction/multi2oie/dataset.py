"""Dataset class used for preparing input to relation extraction model."""

import torch
from torch.utils.data import Dataset

from .other import utils
from .multi2oie_utils import get_cached_tokenizer


class EvalDataset(Dataset):
    def __init__(
        self,
        data_path,
        max_len,
        from_list=True,
        tokenizer_config="bert-base-multilingual-cased",
    ):
        if not from_list:
            self.sentences = utils.load_pkl(data_path)
        else:
            # Data should be a list of sentences (or pickled list of sentences)
            self.sentences = data_path
        self.tokenizer = get_cached_tokenizer(tokenizer_config)
        self.vocab = self.tokenizer.vocab
        self.max_len = max_len

        self.pad_idx = self.vocab["[PAD]"]
        self.cls_idx = self.vocab["[CLS]"]
        self.sep_idx = self.vocab["[SEP]"]
        self.mask_idx = self.vocab["[MASK]"]

    def add_pad(self, token_ids):
        diff = self.max_len - len(token_ids)
        if diff > 0:
            token_ids += [self.pad_idx] * diff
        else:
            token_ids = token_ids[: self.max_len - 1] + [self.sep_idx]
        return token_ids

    def idx2mask(self, token_ids):
        return [token_id != self.pad_idx for token_id in token_ids]

    def __getitem__(self, idx):
        token_ids = self.add_pad(self.tokenizer.encode(self.sentences[idx]))
        att_mask = self.idx2mask(token_ids)
        token_strs = self.tokenizer.convert_ids_to_tokens(token_ids)
        sentence = self.sentences[idx]

        assert len(token_ids) == self.max_len
        assert len(att_mask) == self.max_len
        assert len(token_strs) == self.max_len
        batch = [torch.tensor(token_ids), torch.tensor(att_mask), token_strs, sentence]
        return batch

    def __len__(self):
        return len(self.sentences)

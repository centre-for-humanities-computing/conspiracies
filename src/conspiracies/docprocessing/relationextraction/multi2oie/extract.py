import os
from typing import List

import numpy as np
import torch
from tqdm import tqdm

from .other import bio
from .multi2oie_utils import get_cached_tokenizer


def extract(args, model, loader, output_path):
    model.eval()
    os.makedirs(output_path, exist_ok=True)
    extraction_path = os.path.join(output_path, "extraction.txt")
    tokenizer = get_cached_tokenizer(args["bert_config"])
    f = open(extraction_path, "w")

    for step, batch in tqdm(enumerate(loader), desc="eval_steps", total=len(loader)):
        token_strs = [[word for word in sent] for sent in np.asarray(batch[-2]).T]
        sentences = batch[-1]
        token_ids, att_mask = map(lambda x: x.to(args.device), batch[:-2])

        with torch.no_grad():
            """We will iterate B(batch_size) times because there are more than
            one predicate in one batch. In feeding to argument extractor, # of
            predicates takes a role as batch size.

            pred_logit: (B, L, 3)
            pred_hidden: (B, L, D)
            pred_tags: (B, P, L) ~ list of tensors, where P is # of predicate in each
                batch
            """
            pred_logit, pred_hidden = model.extract_predicate(
                input_ids=token_ids,
                attention_mask=att_mask,
            )
            pred_tags = torch.argmax(pred_logit, 2)
            pred_tags = bio.filter_pred_tags(pred_tags, token_strs)
            pred_tags = bio.get_single_predicate_idxs(pred_tags)
            pred_probs = torch.nn.Softmax(2)(pred_logit)

            # iterate B times (one iteration means extraction for one sentence)
            for (
                cur_pred_tags,
                cur_pred_hidden,
                cur_att_mask,
                cur_token_id,
                cur_pred_probs,
                token_str,
                sentence,
            ) in zip(
                pred_tags,
                pred_hidden,
                att_mask,
                token_ids,
                pred_probs,
                token_strs,
                sentences,
            ):
                # generate temporary batch for this sentence and feed to argument module
                cur_pred_masks = bio.get_pred_mask(cur_pred_tags).to(args.device)
                n_predicates = cur_pred_masks.shape[0]
                if n_predicates == 0:
                    continue  # if there is no predicate, we cannot extract.
                cur_pred_hidden = torch.cat(
                    n_predicates * [cur_pred_hidden.unsqueeze(0)],
                )
                cur_token_id = torch.cat(n_predicates * [cur_token_id.unsqueeze(0)])
                cur_arg_logit = model.extract_argument(
                    input_ids=cur_token_id,
                    predicate_hidden=cur_pred_hidden,
                    predicate_mask=cur_pred_masks,
                )

                # filter and get argument tags with highest probability
                cur_arg_tags = torch.argmax(cur_arg_logit, 2)
                cur_arg_probs = torch.nn.Softmax(2)(cur_arg_logit)
                cur_arg_tags = bio.filter_arg_tags(
                    cur_arg_tags,
                    cur_pred_tags,
                    token_str,
                )

                # get string tuples and write results
                cur_extractions, cur_extraction_idxs = bio.get_tuple(
                    sentence,
                    cur_pred_tags,
                    cur_arg_tags,
                    tokenizer,
                )
                cur_confidences = bio.get_confidence_score(
                    cur_pred_probs,
                    cur_arg_probs,
                    cur_extraction_idxs,
                )
                for extraction, confidence in zip(cur_extractions, cur_confidences):
                    if args.binary:
                        f.write(
                            "\t".join([sentence] + [str(1.0)] + extraction[:3]) + "\n",
                        )
                    else:
                        f.write(
                            "\t".join([sentence] + [str(confidence)] + extraction)
                            + "\n",
                        )
        f.close()
    print("\nExtraction Done.\n")


def extract_to_list(args, model, loader):
    model.eval()
    tokenizer = get_cached_tokenizer(args["bert_config"])

    out = {}
    out["sentence"] = []
    out["confidence"] = []
    out["extraction"] = []
    out["extraction_3"] = []

    for step, batch in tqdm(enumerate(loader), desc="eval_steps", total=len(loader)):
        token_strs = [[word for word in sent] for sent in np.asarray(batch[-2]).T]
        sentences = batch[-1]
        token_ids, att_mask = map(lambda x: x.to(args["device"]), batch[:-2])

        with torch.no_grad():
            """We will iterate B(batch_size) times because there are more than
            one predicate in one batch. In feeding to argument extractor, # of
            predicates takes a role as batch size.

            pred_logit: (B, L, 3)
            pred_hidden: (B, L, D)
            pred_tags: (B, P, L) ~ list of tensors, where P is # of predicate in each
                batch
            """
            pred_logit, pred_hidden = model.extract_predicate(
                input_ids=token_ids,
                attention_mask=att_mask,
            )
            pred_tags = torch.argmax(pred_logit, 2)
            pred_tags = bio.filter_pred_tags(pred_tags, token_strs)
            pred_tags = bio.get_single_predicate_idxs(pred_tags)
            pred_probs = torch.nn.Softmax(2)(pred_logit)

            # iterate B times (one iteration means extraction for one sentence)
            for (
                cur_pred_tags,
                cur_pred_hidden,
                cur_att_mask,
                cur_token_id,
                cur_pred_probs,
                token_str,
                sentence,
            ) in zip(
                pred_tags,
                pred_hidden,
                att_mask,
                token_ids,
                pred_probs,
                token_strs,
                sentences,
            ):
                # generate temporary batch for this sentence and feed to argument module
                cur_pred_masks = bio.get_pred_mask(cur_pred_tags).to(args["device"])
                n_predicates = cur_pred_masks.shape[0]
                if n_predicates == 0:
                    continue  # if there is no predicate, we cannot extract.
                cur_pred_hidden = torch.cat(
                    n_predicates * [cur_pred_hidden.unsqueeze(0)],
                )
                cur_token_id = torch.cat(n_predicates * [cur_token_id.unsqueeze(0)])
                cur_arg_logit = model.extract_argument(
                    input_ids=cur_token_id,
                    predicate_hidden=cur_pred_hidden,
                    predicate_mask=cur_pred_masks,
                )

                # filter and get argument tags with highest probability
                cur_arg_tags = torch.argmax(cur_arg_logit, 2)
                cur_arg_probs = torch.nn.Softmax(2)(cur_arg_logit)
                cur_arg_tags = bio.filter_arg_tags(
                    cur_arg_tags,
                    cur_pred_tags,
                    token_str,
                )

                # get string tuples and write results
                cur_extractions, cur_extraction_idxs = bio.get_tuple(
                    sentence,
                    cur_pred_tags,
                    cur_arg_tags,
                    tokenizer,
                )
                cur_confidences = bio.get_confidence_score(
                    cur_pred_probs,
                    cur_arg_probs,
                    cur_extraction_idxs,
                )
                for extraction, confidence in zip(cur_extractions, cur_confidences):
                    out["sentence"].append(sentence)
                    out["confidence"].append(confidence)
                    out["extraction"].append(extraction)
                    out["extraction_3"].append(extraction[:3])

    print("\nExtraction Done.\n")
    return out


def simple_extract(model, loader, device):
    tokenizer = get_cached_tokenizer("bert-base-multilingual-cased")
    triplet = []
    conf = []
    for step, batch in tqdm(enumerate(loader), desc="eval_steps", total=len(loader)):
        token_strs = [[word for word in sent] for sent in np.asarray(batch[-2]).T]
        sentences = batch[-1]
        token_ids, att_mask = map(lambda x: x.to(device), batch[:-2])

        with torch.no_grad():
            """We will iterate B(batch_size) times because there are more than
            one predicate in one batch. In feeding to argument extractor, # of
            predicates takes a role as batch size.

            pred_logit: (B, L, 3)
            pred_hidden: (B, L, D)
            pred_tags: (B, P, L) ~ list of tensors, where P is # of predicate in each
                batch
            """
            pred_logit, pred_hidden = model.extract_predicate(
                input_ids=token_ids,
                attention_mask=att_mask,
            )
            pred_tags = torch.argmax(pred_logit, 2)
            pred_tags = bio.filter_pred_tags(pred_tags, token_strs)
            pred_tags = bio.get_single_predicate_idxs(pred_tags)
            pred_probs = torch.nn.Softmax(2)(pred_logit)

            # iterate B times (one iteration means extraction for one sentence)
            for (
                cur_pred_tags,
                cur_pred_hidden,
                cur_att_mask,
                cur_token_id,
                cur_pred_probs,
                token_str,
                sentence,
            ) in zip(
                pred_tags,
                pred_hidden,
                att_mask,
                token_ids,
                pred_probs,
                token_strs,
                sentences,
            ):
                # generate temporary batch for this sentence and feed to argument module
                cur_pred_masks = bio.get_pred_mask(cur_pred_tags).to(device)
                n_predicates = cur_pred_masks.shape[0]
                if n_predicates == 0:
                    continue  # if there is no predicate, we cannot extract.
                cur_pred_hidden = torch.cat(
                    n_predicates * [cur_pred_hidden.unsqueeze(0)],
                )
                cur_token_id = torch.cat(n_predicates * [cur_token_id.unsqueeze(0)])
                cur_arg_logit = model.extract_argument(
                    input_ids=cur_token_id,
                    predicate_hidden=cur_pred_hidden,
                    predicate_mask=cur_pred_masks,
                )

                # filter and get argument tags with highest probability
                cur_arg_tags = torch.argmax(cur_arg_logit, 2)
                cur_arg_probs = torch.nn.Softmax(2)(cur_arg_logit)
                cur_arg_tags = bio.filter_arg_tags(
                    cur_arg_tags,
                    cur_pred_tags,
                    token_str,
                )

                # get string tuples and write results
                cur_extractions, cur_extraction_idxs = bio.get_tuple(
                    sentence,
                    cur_pred_tags,
                    cur_arg_tags,
                    tokenizer,
                )
                cur_confidences = bio.get_confidence_score(
                    cur_pred_probs,
                    cur_arg_probs,
                    cur_extraction_idxs,
                )

                tmp_triplet = []
                tmp_confidence = []
                for extraction, confidence in zip(cur_extractions, cur_confidences):
                    tmp_triplet.append(extraction[:3])
                    tmp_confidence.append(confidence)

                triplet.append(tmp_triplet)
                conf.append(tmp_confidence)

    return (triplet, conf)


def extract_to_dict(args, model, loader):
    model.eval()
    tokenizer = get_cached_tokenizer(args["bert_config"])

    out = {}
    out["sentence"] = []
    out["wordpieces"] = []
    out["confidence"] = []
    out["extraction_span"] = []
    out["extraction"] = []

    for step, batch in enumerate(loader):
        token_strs = [[word for word in sent] for sent in np.asarray(batch[-2]).T]
        sentences = batch[-1]
        token_ids, att_mask = map(lambda x: x.to(args["device"]), batch[:-2])

        with torch.no_grad():
            """We will iterate B(batch_size) times because there are more than
            one predicate in one batch. In feeding to argument extractor, # of
            predicates takes a role as batch size.

            pred_logit: (B, L, 3)
            pred_hidden: (B, L, D)
            pred_tags: (B, P, L) ~ list of tensors, where P is # of predicate in each
                batch
            """
            pred_logit, pred_hidden = model.extract_predicate(
                input_ids=token_ids,
                attention_mask=att_mask,
            )
            pred_tags = torch.argmax(pred_logit, 2)
            pred_tags = bio.filter_pred_tags(pred_tags, token_strs)
            pred_tags = bio.get_single_predicate_idxs(pred_tags)
            pred_probs = torch.nn.Softmax(2)(pred_logit)

            # iterate B times (one iteration means extraction for one sentence)
            for (
                cur_pred_tags,
                cur_pred_hidden,
                cur_att_mask,
                cur_token_id,
                cur_pred_probs,
                token_str,
                sentence,
            ) in zip(
                pred_tags,
                pred_hidden,
                att_mask,
                token_ids,
                pred_probs,
                token_strs,
                sentences,
            ):
                # generate temporary batch for this sentence and feed to argument module
                cur_pred_masks = bio.get_pred_mask(cur_pred_tags).to(args["device"])
                n_predicates = cur_pred_masks.shape[0]
                if n_predicates == 0:
                    continue  # if there is no predicate, we cannot extract.
                cur_pred_hidden = torch.cat(
                    n_predicates * [cur_pred_hidden.unsqueeze(0)],
                )
                cur_token_id = torch.cat(n_predicates * [cur_token_id.unsqueeze(0)])
                cur_arg_logit = model.extract_argument(
                    input_ids=cur_token_id,
                    predicate_hidden=cur_pred_hidden,
                    predicate_mask=cur_pred_masks,
                )

                # filter and get argument tags with highest probability
                cur_arg_tags = torch.argmax(cur_arg_logit, 2)
                cur_arg_probs = torch.nn.Softmax(2)(cur_arg_logit)
                cur_arg_tags = bio.filter_arg_tags(
                    cur_arg_tags,
                    cur_pred_tags,
                    token_str,
                )

                # get string tuples and write results
                cur_extractions, cur_extraction_idxs = bio.get_tuple(
                    sentence,
                    cur_pred_tags,
                    cur_arg_tags,
                    tokenizer,
                )
                cur_confidences = bio.get_confidence_score(
                    cur_pred_probs,
                    cur_arg_probs,
                    cur_extraction_idxs,
                )

                def _remove_pad_tokens(wordpieces: List[str]):
                    return [token for token in wordpieces if token != "[PAD]"]

                def _flip_pos(t: tuple):
                    # swap start and end
                    t[0], t[1] = t[1], t[0]  # type: ignore
                    return t

                out["sentence"].append(sentence)
                out["wordpieces"].append(token_str)
                out["confidence"].append(cur_confidences)
                out["extraction_span"].append(
                    [_flip_pos(cur_idx[:3]) for cur_idx in cur_extraction_idxs],
                )
                out["extraction"].append(
                    [
                        _flip_pos(cur_extraction[:3])
                        for cur_extraction in cur_extractions
                    ],
                )

    return out
    return out

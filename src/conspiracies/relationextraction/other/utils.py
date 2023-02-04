import pickle

from ..model import BERTBiLSTM, Multi2OIE


def get_models(
    bert_config,
    pred_n_labels=3,
    arg_n_labels=9,
    n_arg_heads=8,
    n_arg_layers=4,
    lstm_dropout=0.3,
    mh_dropout=0.1,
    pred_clf_dropout=0.0,
    arg_clf_dropout=0.3,
    pos_emb_dim=64,
    use_lstm=False,
    device=None,
):
    if not use_lstm:
        return Multi2OIE(
            bert_config=bert_config,
            mh_dropout=mh_dropout,
            pred_clf_dropout=pred_clf_dropout,
            arg_clf_dropout=arg_clf_dropout,
            n_arg_heads=n_arg_heads,
            n_arg_layers=n_arg_layers,
            pos_emb_dim=pos_emb_dim,
            pred_n_labels=pred_n_labels,
            arg_n_labels=arg_n_labels,
        ).to(device)
    else:
        return BERTBiLSTM(
            bert_config=bert_config,
            lstm_dropout=lstm_dropout,
            pred_clf_dropout=pred_clf_dropout,
            arg_clf_dropout=arg_clf_dropout,
            pos_emb_dim=pos_emb_dim,
            pred_n_labels=pred_n_labels,
            arg_n_labels=arg_n_labels,
        ).to(device)


def load_pkl(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def get_word2piece(sentence, tokenizer):
    words = sentence.split(" ")
    word2piece = {idx: list() for idx in range(len(words))}
    sentence_pieces = list()
    piece_idx = 1
    for word_idx, word in enumerate(words):
        pieces = tokenizer.tokenize(word)
        sentence_pieces += pieces
        for piece_idx_added, piece in enumerate(pieces):
            word2piece[word_idx].append(piece_idx + piece_idx_added)
        piece_idx += len(pieces)
    assert len(sentence_pieces) == piece_idx - 1
    return word2piece

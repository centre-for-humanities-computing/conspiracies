"""Functions for creating prompt templates."""

from typing import Tuple, List


def prompt_template_1(
    examples: List[Tuple],
    target_tweet: str,
    introduction: str,
) -> str:
    """Create a prompt template on the form

    '''
    {Introduction}
    Tweet: {tweet1}
    Triplet: {triplets1}
    ...
    Tweet: {tweetN}
    Triplet: {tripletsN}

    Tweet: {target_tweet}
    '''
    """

    examples_str = "---\n\n"
    for tweet, triplets in examples:
        examples_str += f"Tweet: {tweet}\n\n"

        if len(triplets) == 0:
            examples_str += f"Triplet: Null \n"
        else:
            for i, triplet in enumerate(triplets):
                assert len(triplet) == 3, "len of triplets should be 3"
                triplet_str = f"({triplet[0]}) ({triplet[1]}) ({triplet[2]})"
                if i == 0:
                    examples_str += f"Triplet: {triplet_str}\n"
                else:
                    examples_str += f"\t{triplet_str}\n"

        examples_str += "\n---\n\n"

    return f"{introduction}\n\n{examples_str}\nTweet: {target_tweet}\n\nTriplets:"


def prompt_template_2(
    examples: List[Tuple],
    target_tweet: str,
    introduction: str,
) -> str:
    """Create a prompt template on the form

    '''
    {Introduction}
    Tweet: {tweet1}
    Tweet: {tweet2}
    ...
    Tweet: {tweetN}

    Triplet: {triplets1}
    Triplet: {triplets2}
    ...
    Triplet: {tripletsN}

    Tweet: {target_tweet}
    '''
    """

    tweets_block = "---\n\n"
    tweets, tweet_triplets = zip(*examples)

    for tweet in tweets:
        tweets_block += f"Tweet: {tweet}\n\n"

    tweet_triplet_str = ""
    for triplets in tweet_triplets:
        for i, triplet in enumerate(triplets):
            assert len(triplet) == 3, "len of triplets should be 3"
            triplet_str = f"({triplet[0]}) ({triplet[1]}) ({triplet[2]})"
            if i == 0:
                tweet_triplet_str += f"Triplet: {triplet_str}\n"
            else:
                tweet_triplet_str += f"\t{triplet_str}\n"
    tweet_triplet_str += "\n---\n\n"

    return f"{introduction}\n\n{tweets_block}\n{tweet_triplet_str}\nTweet: {target_tweet}\n\nTriplets:"


def prompt_template_3(
    examples: List[Tuple],
    target_tweet: str,
    introduction: str,
) -> str:
    """Create a prompt template on the form

    '''
    {introduction}

    | Tweet | Subject | Predicate | Object |
    | --- | --- | --- | --- |
    | {tweet 1} | {subject 1} | {predicate 1} | {object 1} |
    | {tweet 1} | {subject 2} | {predicate 2} | {object 2} |
    ...
    | {tweet n} | {subject 1} | {predicate 1} | {object 1} |
    | {tweet n} | {subject 2} | {predicate 2} | {object 2} |
    | {target_tweet} |

    '''
    """
    tweet_string = f"{introduction}\n| Tweet | Subject | Predicate | Object |\n| --- | --- | --- | --- |"
    for example, triplets in examples:
        for i, triplet in enumerate(triplets):
            assert len(triplet) == 3, "len of triplets should be 3"
            if i == 0:
                tweet_string += (
                    f"\n| {example} | {triplet[0]} | {triplet[1]} | {triplet[2]} |"
                )
            else:
                tweet_string += f"\n| | {triplet[0]} | {triplet[1]} | {triplet[2]} |"
    tweet_string += f"\n| {target_tweet} |"
    return tweet_string


def prompt_template_4(
    examples: List[Tuple],
    target_tweet: str,
    introduction: str,
) -> str:
    """Create a prompt template on the form

    '''
    {Task description}

    {tweet 1}

    | Subject | Predicate | Object |
    | ---- | ---- | ---- |
    | {triplet 1 from tweet 1}
    | {triplet 2 from tweet 1}

    {tweet 2}

    | Subject | Predicate | Object |
    | ---- | ---- | ---- |
    | {triplet 1 from tweet 2}
    | {triplet 2 from tweet 2}
    ...

    {target tweet}

    | Subject | Predicate | Object |
    | ---- | ---- | ---- |
    '''

    """
    header = "| Subject | Predicate | Object |\n| --- | --- | --- |"
    tweet_string = f"{introduction}\n\n"
    for example, triplets in examples:
        tweet_string += example + "\n\n" + header
        for triplet in triplets:
            tweet_string += f"\n| {triplet[0]} | {triplet[1]} | {triplet[2]} |"
        tweet_string += "\n\n"
    tweet_string += target_tweet + "\n\n" + header + "\n"
    return tweet_string

def prompt_template_5(
    examples: List[Tuple],
    target_tweet: str,
    introduction: str,
) -> str:
    """Create a prompt template on the form

    {introduction}

    {tweet 1}
    {html_tagged tweet 1}

    ...

    {tweet n}
    {html_tagged tweet n}

    {target tweet}
    """

    tweet_string = f"{introduction}\n\n"
    for example, html in examples:
        tweet_string += example + "\n" + html + "\n\n"
    
    tweet_string += target_tweet + "\n"
    return tweet_string
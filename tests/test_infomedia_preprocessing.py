from conspiracies.preprocessing.infomedia import InfoMediaPreprocessor


def test_create_text():
    input_text = {
        "Heading": "Nice title",
        "SubHeading": "With a nice subtitle",
        "BodyText": "<p>One paragraph</p>"
        "<p>Another paragraph</p>"
        "<p><br/>A third with a line break and <em>emphasis</em>.</p>",
    }
    text = InfoMediaPreprocessor.create_text(input_text)

    expected = (
        "Nice title\n\n"
        "With a nice subtitle\n\n"
        "One paragraph\n"
        "Another paragraph\n\n"
        "A third with a line break and emphasis."
    )

    assert text == expected

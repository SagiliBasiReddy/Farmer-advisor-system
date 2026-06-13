def prefer_crop_specific(candidates, crop):
    if not candidates:
        return None

    if not crop:
        return candidates[0]

    crop = crop.lower()
    crop_specific = []
    generic = []

    for c in candidates:
        q = c["question"].lower()
        # Join all answer texts since answers is now a list of dicts
        answers_text = " ".join([ans["text"] for ans in c["answers"]]).lower()

        if crop in q or crop in answers_text:
            crop_specific.append(c)
        else:
            generic.append(c)

    return crop_specific[0] if crop_specific else generic[0]

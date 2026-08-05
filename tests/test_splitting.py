from k2_nli.splitting import split_general_by_context


def test_contexts_do_not_leak_between_splits():
    records = []
    for domain in ("medical", "finance", "legal"):
        for context_index in range(80):
            context_id = f"{domain}_{context_index}"
            for label in ("supported", "partially_supported", "contradicted", "unverifiable"):
                records.append({"context_id": context_id, "domain": domain, "gold_label": label})
    splits = split_general_by_context(records, seed=42)
    context_sets = [{x["context_id"] for x in values} for values in splits.values()]
    assert context_sets[0].isdisjoint(context_sets[1])
    assert context_sets[0].isdisjoint(context_sets[2])
    assert context_sets[1].isdisjoint(context_sets[2])
    assert sum(len(x) for x in context_sets) == 240

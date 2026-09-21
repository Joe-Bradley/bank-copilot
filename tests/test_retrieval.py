from retrieval import retrieve_product_context


def test_known_product_returns_context():
    context = retrieve_product_context(
        "星河成长账户最低起存金额是多少？"
    )

    assert context is not None
    assert "星河成长账户" in context
    assert "100元" in context


def test_unknown_product_returns_none():
    context = retrieve_product_context(
        "月亮账户最低起存金额是多少？"
    )

    assert context is None


def test_multiple_products_return_all_context():
    context = retrieve_product_context(
        "比较星河成长账户和稳享养老存款的最低起存金额"
    )

    assert context is not None
    assert "星河成长账户" in context
    assert "100元" in context
    assert "稳享养老存款" in context
    assert "10,000元" in context


def test_product_aliases_do_not_duplicate_context():
    context = retrieve_product_context(
        "星河成长账户和成长账户有什么区别？"
    )

    assert context is not None
    assert context.count("## 星河成长账户") == 1
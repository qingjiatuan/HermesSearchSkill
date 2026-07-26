# Adapters - 延迟导入，避免循环依赖
def get_union_search_adapter():
    from adapters.union_search_adapter import UnionSearchAdapter
    return UnionSearchAdapter
def get_anysearch_adapter():
    from adapters.anysearch_adapter import AnySearchAdapter
    return AnySearchAdapter

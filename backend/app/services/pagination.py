def paginate_query(query, limit: int, offset: int):
    total = query.order_by(None).count()
    items = query.offset(offset).limit(limit).all()

    return items, total

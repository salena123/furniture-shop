def serialize_user(user):
    if user is None:
        return None

    return {
        "id": user.id,
        "login": user.login,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "last_login_at": user.last_login_at,
    }


def serialize_product_image(image):
    return {
        "id": image.id,
        "product_id": image.product_id,
        "image_url": image.image_url,
        "alt_text": image.alt_text,
        "sort_order": image.sort_order,
        "is_main": image.is_main,
    }


def serialize_product_attribute(product_attribute):
    attribute_value = product_attribute.attribute_value
    attribute = attribute_value.attribute if attribute_value else None

    return {
        "id": attribute_value.id,
        "attribute_id": attribute_value.attribute_id,
        "attribute_name": attribute.name if attribute else None,
        "value": attribute_value.value,
        "sort_order": attribute_value.sort_order,
    }


def serialize_product(product):
    if product is None:
        return None

    images = sorted(
        product.images or [],
        key=lambda image: (image.sort_order, image.id),
    )
    product_attributes = sorted(
        product.product_attributes or [],
        key=lambda product_attribute: (
            product_attribute.attribute_value.sort_order,
            product_attribute.attribute_value.id,
        ),
    )

    material_ref = product.material_ref

    return {
        "id": product.id,
        "product_name": product.product_name,
        "slug": product.slug,
        "description": product.description,
        "short_description": product.short_description,
        "article": product.article,
        "category_id": product.category_id,
        "material_id": product.material_id,
        "material_name": material_ref.name if material_ref else product.material,
        "price": product.price,
        "material": product.material,
        "is_custom": product.is_custom,
        "is_active": product.is_active,
        "sort_order": product.sort_order,
        "dimensions": product.dimensions,
        "color": product.color,
        "meta_title": product.meta_title,
        "meta_description": product.meta_description,
        "images": [
            serialize_product_image(image)
            for image in images
        ],
        "attributes": [
            serialize_product_attribute(product_attribute)
            for product_attribute in product_attributes
        ],
    }


def serialize_comment(comment):
    user = comment.user

    return {
        "id": comment.id,
        "request_id": comment.request_id,
        "user_id": comment.user_id,
        "user_name": user.name if user else None,
        "user_role": user.role if user else None,
        "comment_text": comment.comment_text,
        "created_at": comment.created_at,
    }


def serialize_request_event(event):
    user = event.user

    return {
        "id": event.id,
        "request_id": event.request_id,
        "user_id": event.user_id,
        "user_name": user.name if user else None,
        "user_role": user.role if user else None,
        "event_type": event.event_type,
        "old_status": event.old_status,
        "new_status": event.new_status,
        "message": event.message,
        "created_at": event.created_at,
    }


def serialize_request(request):
    manager = request.assigned_manager
    material = request.material
    product = request.product
    category = product.category if product else None
    product_name = product.product_name if product else request.product_name
    color_name = request.color_name or (product.color if product else None)

    return {
        "id": request.id,
        "product_id": request.product_id,
        "product_slug": product.slug if product else None,
        "category_id": product.category_id if product else None,
        "category_name": category.name if category else None,
        "material_id": request.material_id,
        "material_name": material.name if material else None,
        "product_name": product_name,
        "color_name": color_name,
        "needs_measurements": request.needs_measurements,
        "dimensions": request.dimensions,
        "client_name": request.client_name,
        "phone": request.phone,
        "city": request.city,
        "preferred_contact_time": request.preferred_contact_time,
        "personal_data_consent": request.personal_data_consent,
        "status": request.status,
        "assigned_manager_id": request.assigned_manager_id,
        "assigned_manager_name": manager.name if manager else None,
        "comment": request.comment,
        "created_at": request.created_at,
        "updated_at": request.updated_at,
        "contacted_at": request.contacted_at,
        "completed_at": request.completed_at,
        "comments_count": len(request.comments or []),
        "events_count": len(request.events or []),
    }


def serialize_request_detail(request):
    details = serialize_request(request)
    details["assigned_manager"] = serialize_user(request.assigned_manager)
    details["product"] = serialize_product(request.product)
    details["comments"] = [
        serialize_comment(comment)
        for comment in sorted(
            request.comments or [],
            key=lambda comment: (comment.created_at, comment.id),
        )
    ]
    details["events"] = [
        serialize_request_event(event)
        for event in sorted(
            request.events or [],
            key=lambda event: (event.created_at, event.id),
        )
    ]
    return details

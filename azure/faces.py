def show_similar_faces(img_one_path, img_one_face, img_two_path, img_two_faces, similar_faces):
    import matplotlib.pyplot as plt
    from PIL import Image, ImageDraw

    fig = plt.figure(figsize=(16, 6))

    # Show face 1
    img_one = Image.open(img_one_path)
    r = img_one_face.face_rectangle
    bounding_box = ((r.left, r.top), (r.left + r.width, r.top + r.height))
    draw = ImageDraw.Draw(img_one)
    draw.rectangle(bounding_box, outline='magenta', width=5)
    a = fig.add_subplot(1, 2, 1)
    plt.axis('off')
    plt.imshow(img_one)

    # Get the matching face IDs
    matching_face_ids = list(map(lambda face: face.face_id, similar_faces))

    # Draw a rectangle around each similar face in image 2
    img_two = Image.open(img_two_path)
    a = fig.add_subplot(1, 2, 2)
    plt.axis('off')
    for face in img_two_faces:
        r = face.face_rectangle
        bounding_box = ((r.left, r.top), (r.left + r.width, r.top + r.height))
        draw = ImageDraw.Draw(img_two)
        if face.face_id in matching_face_ids:
            draw.rectangle(bounding_box, outline='lightgreen', width=10)
            plt.annotate('Match!', (r.left, r.top + r.height + 15), backgroundcolor='white')
        else:
            draw.rectangle(bounding_box, outline='red', width=5)
    plt.imshow(img_two)
    plt.show()

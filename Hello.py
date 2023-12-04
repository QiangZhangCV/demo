import streamlit as st
from PIL import Image
import streamlit_image_comparison as sic
import numpy as np
import imageio

session_state = st.session_state

st.sidebar.title('Image Comparison')

# Upload the images in the sidebar
uploaded_files = st.sidebar.file_uploader("Upload Two Image Files", type=["jpg", "png", "jpeg", "gif", "bmp"], accept_multiple_files=True)

# Add a checkbox in the sidebar to toggle the display of labels
show_labels = st.sidebar.checkbox('Show labels', value=True)

# Add text input in the sidebar for the labels
label1 = st.sidebar.text_input('Label for the left image', value="Before") if show_labels else ""
label2 = st.sidebar.text_input('Label for the left image', value="After") if show_labels else ""

images = [Image.open(file) for file in uploaded_files]

if len(images) < 2:
    st.error('Please Upload Two Image Files')
elif len(images) > 2:
    st.error('Uploaded Image File Number Exceeds Two.')
else:
    if 'swap' not in session_state:
        session_state.swap = False

    # Add a button to swap the images
    if st.sidebar.button('Swap Image Positions'):
        session_state.swap = not session_state.swap

    # Swap the images and labels if necessary
    if session_state.swap:
        images.reverse()
        label1, label2 = label2, label1
        
    # width = min(images[0].size[0], images[1].size[0], 700)
    width = 700
    comparison_image = sic.image_comparison(images[0], images[1], label1, label2, width=width, starting_position=50)
    
    if  st.sidebar.button('Generate GIF'):
        # Create a list to store the frames of the GIF
        with st.spinner('GIF生成中...'):
            frames = []

            img1 = np.array(images[0].convert('RGB'))
            img2 = np.array(images[1].convert('RGB'))
            
            if img1.shape[0] > 450:
                new_height = int(img1.shape[1] *450 / img1.shape[0])
                img1 = np.array(Image.fromarray(img1).resize((450, new_height)))
            
            # Resize the second image to match the first image
            img2 = np.array(Image.fromarray(img2).resize(img1.shape[1::-1]))
            
            # Generate the frames
            for i in range(101):
                # Calculate the width for the first image
                width1 = int(i * img1.shape[1] / 100)

                # Create the combined image
                combined = np.concatenate((img1[:, :img1.shape[1]-width1], img2[:, img1.shape[1]-width1:]), axis=1)
                if  2<width1<img1.shape[1]-2:
                    combined[:, img1.shape[1]-width1-2 :img1.shape[1]-width1+2, : ] = 255

                # Convert the combined image to a PIL Image and add it to the frames
                frames.append(Image.fromarray(combined))

            # Create the GIF
            imageio.mimsave('comparison.gif', frames, 'GIF', loop=0, duration=30)
        st.success('GIF已生成, 可鼠标右键下载')
        st.image('comparison.gif')

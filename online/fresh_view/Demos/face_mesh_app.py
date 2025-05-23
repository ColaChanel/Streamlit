import streamlit as st
import mediapipe as mp
import cv2
import numpy as np
import tempfile
import time
from PIL import Image
# код для gpu?
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Выберите нужное вам устройство GPU

mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

DEMO_VIDEO = 'fresh_view\Demos\demo.mp4'
DEMO_IMAGE = 'fresh_view\Demos\demo.jpg'

st.title('Нанесение лицевой сетки')

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 350px;
        margin-left: -350px;

    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 350px;
        margin-left: -350px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title('Нанесение лицевой сетки')
st.sidebar.subheader('Параметры')

@st.cache_data()
def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation=inter)

    return resized

app_mode = st.sidebar.selectbox('Выберите вид взаимодействия',
['О приложении','Запустить по видео']
# 'Запустить по картинке',
)
if app_mode =='О приложении':

    st.markdown('В этом приложении мы используем **MediaPipe** для создания маски лица. **Streamlit** для создания Веб графического пользовательского  Интерфейса')
    st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 400px;
        margin-left: -400px;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )
    st.markdown('''
                Где может быть применим проект:
                - Безопасность и идентификация
                - Медицинская диагностика
                - Образование
                - Приложения дополненной реальности (AR)
                ''')

    st.markdown('''
          # Обо мне \n 
            Привет я  Коновалов Игорь  начинающий Data-Scientist. \n
           
            Если вы заинтересованы в построении  приложений компьютерного зрения(CV) как это вы можете написать мне, и мы можем обсудить вопрос дальнейшего сотрудничества. Мой телеграм: [@ColaChanel](https://t.me/ColaChannel)
             \n
            
            Также можете связаться со мной:
            - [LinkedIn](https://www.linkedin.com/in/igorkonovalovvasko/)
            - [gmail](mailto:igor.konovalov.dev@gmail.com/)
            - [Github](https://github.com/ColaChanel)
        
            
             
            ''')
    # Если ты чувствуешь себя великодушным, то можешь купить мне  **чашку кофе** от [сюда](https://www.buymeacoffee.com/colachanel)
# if app_mode =='About App':
#     st.markdown('In this application we are using **MediaPipe** for creating a Face Mesh. **StreamLit** is to create the Web Graphical User Interface (GUI) ')
#     st.markdown(
#     """
#     <style>
#     [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
#         width: 400px;
#     }
#     [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
#         width: 400px;
#         margin-left: -400px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
#     )
#     st.video('https://www.youtube.com/watch?v=FMaNNXgB_5c&ab_channel=AugmentedStartups')

#     st.markdown('''
#           # About Me \n 
#             Hey this is ** Ritesh Kanjee ** from **Augmented Startups**. \n
           
#             If you are interested in building more Computer Vision apps like this one then visit the **Vision Store** at
#             www.augmentedstartups.info/visionstore \n
            
#             Also check us out on Social Media
#             - [YouTube](https://augmentedstartups.info/YouTube)
#             - [LinkedIn](https://augmentedstartups.info/LinkedIn)
#             - [Facebook](https://augmentedstartups.info/Facebook)
#             - [Discord](https://augmentedstartups.info/Discord)
        
#             If you are feeling generous you can buy me a **cup of  coffee ** from [HERE](https://augmentedstartups.info/ByMeACoffee)
             
#             ''')
if app_mode =='Запустить по видео':

    # st.set_option('deprecation.showfileUploaderEncoding', False)

    use_webcam = st.sidebar.button('Использовать камеру')
    record = st.sidebar.checkbox("Записать видео")
    if record:
        st.checkbox("Запись", value=True)

    # st.sidebar.markdown('---')
    # st.markdown(
    # """
    # <style>
    # [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
    #     width: 400px;
    # }
    # [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
    #     width: 400px;
    #     margin-left: -400px;
    # }
    # </style>
    # """,
    # unsafe_allow_html=True,
    #     )
    # max faces
    max_faces = st.sidebar.number_input('Максимальное количество лиц', value=1, min_value=1)
    st.sidebar.markdown('---')
    detection_confidence = st.sidebar.slider('Минимальная точность детекции', min_value =0.0,max_value = 1.0,value = 0.5)
    tracking_confidence = st.sidebar.slider('Минимальная уверенность при отслеживании', min_value = 0.0,max_value = 1.0,value = 0.5)

    st.sidebar.markdown('---')

    st.markdown(' ## Выход')

    stframe = st.empty()
    video_file_buffer = st.sidebar.file_uploader("Загрузить видео", type=[ "mp4", "mov",'avi','asf', 'm4v' ])
    tfflie = tempfile.NamedTemporaryFile(delete=False)


    if not video_file_buffer:
        if use_webcam:
            vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            vid = cv2.VideoCapture(DEMO_VIDEO)
            tfflie.name = DEMO_VIDEO
    
    else:
        tfflie.write(video_file_buffer.read())
        vid = cv2.VideoCapture(tfflie.name)

    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_input = int(vid.get(cv2.CAP_PROP_FPS))

    #codec = cv2.VideoWriter_fourcc(*FLAGS.output_format)
    codec = cv2.VideoWriter_fourcc('V','P','0','9')
    out = cv2.VideoWriter('output1.mp4', codec, fps_input, (width, height))

    st.sidebar.text('Входящее Видео')
    # st.sidebar.video(tfflie.name)
    fps = 0
    i = 0
    drawing_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=2)

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.markdown("**Частота кадров**")
        kpi1_text = st.markdown("0")

    with kpi2:
        st.markdown("**Обнаруженны лица**")
        kpi2_text = st.markdown("0")

    with kpi3:
        st.markdown("**размер изображения**")
        kpi3_text = st.markdown("0")

    st.markdown("<hr/>", unsafe_allow_html=True)

    with mp_face_mesh.FaceMesh(
    min_detection_confidence=detection_confidence,
    min_tracking_confidence=tracking_confidence , 
    max_num_faces = max_faces) as face_mesh:
        prevTime = 0
# здесь добавить gpu, под новые реали.
        while vid.isOpened():
            i +=1
            ret, frame = vid.read()
            if not ret:
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = face_mesh.process(frame)

            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            face_count = 0
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    face_count += 1
                    mp_drawing.draw_landmarks(
                    image = frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)
            currTime = time.time()
            fps = 1 / (currTime - prevTime)
            prevTime = currTime
            if record:
                out.write(frame)
            #Dashboard
            kpi1_text.write(f"<h1 style='text-align: center; color: red;'>{int(fps)}</h1>", unsafe_allow_html=True)
            kpi2_text.write(f"<h1 style='text-align: center; color: red;'>{face_count}</h1>", unsafe_allow_html=True)
            kpi3_text.write(f"<h1 style='text-align: center; color: red;'>{width}</h1>", unsafe_allow_html=True)

            frame = cv2.resize(frame,(0,0),fx = 0.8 , fy = 0.8)
            frame = image_resize(image = frame, width = 640)
            stframe.image(frame,channels = 'BGR',use_container_width=True)

    st.text('Видео в обработке')

    output_video = open('output1.mp4','rb')
    out_bytes = output_video.read()
    st.video(out_bytes)

    vid.release()
    out. release()
# if app_mode =='Run on Video':

#     st.set_option('deprecation.showfileUploaderEncoding', False)

#     use_webcam = st.sidebar.button('Use Webcam')
#     record = st.sidebar.checkbox("Record Video")
#     if record:
#         st.checkbox("Recording", value=True)

#     # st.sidebar.markdown('---')
#     # st.markdown(
#     # """
#     # <style>
#     # [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
#     #     width: 400px;
#     # }
#     # [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
#     #     width: 400px;
#     #     margin-left: -400px;
#     # }
#     # </style>
#     # """,
#     # unsafe_allow_html=True,
#     #     )
#     # max faces
#     max_faces = st.sidebar.number_input('Maximum Number of Faces', value=1, min_value=1)
#     st.sidebar.markdown('---')
#     detection_confidence = st.sidebar.slider('Min Detection Confidence', min_value =0.0,max_value = 1.0,value = 0.5)
#     tracking_confidence = st.sidebar.slider('Min Tracking Confidence', min_value = 0.0,max_value = 1.0,value = 0.5)

#     st.sidebar.markdown('---')

#     st.markdown(' ## Output')

#     stframe = st.empty()
#     video_file_buffer = st.sidebar.file_uploader("Upload a video", type=[ "mp4", "mov",'avi','asf', 'm4v' ])
#     tfflie = tempfile.NamedTemporaryFile(delete=False)


#     if not video_file_buffer:
#         if use_webcam:
#             vid = cv2.VideoCapture(0)
#         else:
#             vid = cv2.VideoCapture(DEMO_VIDEO)
#             tfflie.name = DEMO_VIDEO
    
#     # else:
#     #     tfflie.write(video_file_buffer.read())
#     #     vid = cv2.VideoCapture(tfflie.name)

#     width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps_input = int(vid.get(cv2.CAP_PROP_FPS))

#     #codec = cv2.VideoWriter_fourcc(*FLAGS.output_format)
#     codec = cv2.VideoWriter_fourcc('V','P','0','9')
#     out = cv2.VideoWriter('output1.mp4', codec, fps_input, (width, height))

#     st.sidebar.text('Input Video')
#     st.sidebar.video(tfflie.name)
#     fps = 0
#     i = 0
#     drawing_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=2)

#     kpi1, kpi2, kpi3 = st.columns(3)

#     with kpi1:
#         st.markdown("**FrameRate**")
#         kpi1_text = st.markdown("0")

#     with kpi2:
#         st.markdown("**Detected Faces**")
#         kpi2_text = st.markdown("0")

#     with kpi3:
#         st.markdown("**Image Width**")
#         kpi3_text = st.markdown("0")

#     st.markdown("<hr/>", unsafe_allow_html=True)

#     with mp_face_mesh.FaceMesh(
#     min_detection_confidence=detection_confidence,
#     min_tracking_confidence=tracking_confidence , 
#     max_num_faces = max_faces) as face_mesh:
#         prevTime = 0

#         while vid.isOpened():
#             i +=1
#             ret, frame = vid.read()
#             if not ret:
#                 continue

#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = face_mesh.process(frame)

#             frame.flags.writeable = True
#             frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

#             face_count = 0
#             if results.multi_face_landmarks:
#                 for face_landmarks in results.multi_face_landmarks:
#                     face_count += 1
#                     mp_drawing.draw_landmarks(
#                     image = frame,
#                     landmark_list=face_landmarks,
#                     connections=mp_face_mesh.FACEMESH_TESSELATION,
#                     landmark_drawing_spec=drawing_spec,
#                     connection_drawing_spec=drawing_spec)
#             currTime = time.time()
#             fps = 1 / (currTime - prevTime)
#             prevTime = currTime
#             if record:
#                 #st.checkbox("Recording", value=True)
#                 out.write(frame)
#             #Dashboard
#             kpi1_text.write(f"<h1 style='text-align: center; color: red;'>{int(fps)}</h1>", unsafe_allow_html=True)
#             kpi2_text.write(f"<h1 style='text-align: center; color: red;'>{face_count}</h1>", unsafe_allow_html=True)
#             kpi3_text.write(f"<h1 style='text-align: center; color: red;'>{width}</h1>", unsafe_allow_html=True)

#             frame = cv2.resize(frame,(0,0),fx = 0.8 , fy = 0.8)
#             frame = image_resize(image = frame, width = 640)
#             stframe.image(frame,channels = 'BGR',use_column_width=True)

#     st.text('Video Processed')

#     output_video = open('output1.mp4','rb')
#     out_bytes = output_video.read()
#     st.video(out_bytes)

#     vid.release()
#     out. release()

# elif app_mode =='Run on Image':

#     drawing_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=1)

#     st.sidebar.markdown('---')

#     st.markdown(
#     """
#     <style>
#     [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
#         width: 400px;
#     }
#     [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
#         width: 400px;
#         margin-left: -400px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
#     st.markdown("**Detected Faces**")
#     kpi1_text = st.markdown("0")
#     st.markdown('---')

#     max_faces = st.sidebar.number_input('Maximum Number of Faces', value=2, min_value=1)
#     st.sidebar.markdown('---')
#     detection_confidence = st.sidebar.slider('Min Detection Confidence', min_value =0.0,max_value = 1.0,value = 0.5)
#     st.sidebar.markdown('---')

#     img_file_buffer = st.sidebar.file_uploader("Upload an image", type=[ "jpg", "jpeg",'png'])

#     if img_file_buffer is not None:
#         image = np.array(Image.open(img_file_buffer))

#     else:
#         demo_image = DEMO_IMAGE
#         image = np.array(Image.open(demo_image))

#     st.sidebar.text('Original Image')
#     st.sidebar.image(image)
#     face_count = 0
#     # Dashboard
#     with mp_face_mesh.FaceMesh(
#     static_image_mode=True,
#     max_num_faces=max_faces,
#     min_detection_confidence=detection_confidence) as face_mesh:

#         results = face_mesh.process(image)
#         out_image = image.copy()

#         for face_landmarks in results.multi_face_landmarks:
#             face_count += 1

#             #print('face_landmarks:', face_landmarks)

#             mp_drawing.draw_landmarks(
#             image=out_image,
#             landmark_list=face_landmarks,
#             connections=mp_face_mesh.FACE_CONNECTIONS,
#             landmark_drawing_spec=drawing_spec,
#             connection_drawing_spec=drawing_spec)
#             kpi1_text.write(f"<h1 style='text-align: center; color: red;'>{face_count}</h1>", unsafe_allow_html=True)
#         st.subheader('Output Image')
#         st.image(out_image,use_column_width= True)

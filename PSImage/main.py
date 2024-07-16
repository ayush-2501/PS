'''from gradio_client import Client, file
import warnings
warnings.filterwarnings('ignore')

client = Client("lllyasviel/IC-Light")
result = client.predict(
		input_fg=file('i1.webp'),
		prompt="beautiful woman, detailed face, sunshine, outdoor, warm atmosphere",
		image_width=512,
		image_height=960,
		num_samples=1,
		seed=12345,
		steps=25,
		a_prompt="best quality",
		n_prompt="lowres, bad anatomy, bad hands, cropped, worst quality",
		cfg=2,
		highres_scale=1.5,
		highres_denoise=0.5,
		lowres_denoise=0.9,
		bg_source="Right Light",
		api_name="/process_relight"
)
print(result)'''

import time
from gradio_client import Client, handle_file

client = Client("ProductScope/Relight")

start_time = time.time()

result = client.predict(
        input_fg=handle_file('i1.png'),
        prompt="beautiful woman, detailed face, sunshine, outdoor, warm atmosphere",
        image_width=1024,
        image_height=1024,
        num_samples=1,
        steps=40,
        a_prompt="best quality",
        n_prompt="lowres, bad anatomy, bad hands, cropped, worst quality",
        cfg=2,
        highres_scale=1,
        highres_denoise=0.5,
        lowres_denoise=0.9,
        bg_source="Right Light",
        api_name="/process_relight"
)

end_time = time.time()


print(result[1][0]['image'])

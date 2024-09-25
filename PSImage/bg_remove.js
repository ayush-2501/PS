/*import { Client } from "@gradio/client";

const response_0 = await fetch("https://not-lain-background-removal.hf.space/file=/tmp/gradio/7bff8d8799f857675a1cb06effbe5f4cca80944617fc955cbe2988803fd4791a/image.webp");
const exampleImage = await response_0.blob();
						
const client = await Client.connect("not-lain/background-removal");
const result = await client.predict("/image", { 
				image: exampleImage, 
});

console.log(result.data[0][0].url);*/

import { Client } from "@gradio/client";

const response_0 = await fetch("https://kwai-kolors-kolors-virtual-try-on.hf.space/file=/tmp/gradio/9204e4e7f7919583ebb6f3b988e5cbb0ca1d9f7c/000.png");
const exampleImage_1 = await response_0.blob();
						
const response_1 = await fetch("https://kwai-kolors-kolors-virtual-try-on.hf.space/file=/tmp/gradio/4ad0ace4ff53aca8c64e927496827312c7f3a453/07_upper.png");
const exampleImage_2 = await response_1.blob();
						
const client = await Client.connect("Kwai-Kolors/Kolors-Virtual-Try-On");
const result = await client.predict("/tryon", { 
				person_img: exampleImage_1, 
				garment_img: exampleImage_2, 		
		seed: 0, 		
		randomize_seed: true, 
});

console.log(result.data[0].url);

import { Client } from "@gradio/client";

const response_0 = await fetch("https://not-lain-background-removal.hf.space/file=/tmp/gradio/7bff8d8799f857675a1cb06effbe5f4cca80944617fc955cbe2988803fd4791a/image.webp");
const exampleImage = await response_0.blob();
						
const client = await Client.connect("not-lain/background-removal");
const result = await client.predict("/image", { 
				image: exampleImage, 
});

console.log(result.data[0][0].url);

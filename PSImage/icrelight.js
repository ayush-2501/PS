import { Client } from "@gradio/client";

const response_0 = await fetch("https://lllyasviel-ic-light.hf.space/file=/tmp/gradio/53e64423f750364aee2178ddebe719c7acbd1bb0/i10.png");
const exampleImage = await response_0.blob();
						
const app = await Client.connect("lllyasviel/IC-Light");
const result = await app.predict("/process_relight", [
				exampleImage, 	// 'Image'	
				"beautiful woman, detailed face, light and shadow", // 'Prompt'		
				1024, // 'Image Width'		
				1024, // 'Image Height'		
				1, // 'Images'	
				-1, // 'Seed'		
				40, // 'Steps' 	
				"best quality", // 'Added Prompt'	
				"lowres, bad anatomy, bad hands, cropped, worst quality", // 'Negative Prompt'		
				2, // 'CFG Scale'
				1.5, // 'Highres Scale' 
				0.5, // 'Highres Denoise'
				0.9, // 'Lowres Denoise (for initial latent)'	
				"Left Light", // 'Lighting Preference (Initial Latent)' 
	]);

// Output
const outputGalleryValues = result.data[1];
console.log(outputGalleryValues);
import {v2 as cloudinary} from 'cloudinary'
import { response } from 'express';
import fs from 'fs' // for cleaning purpose from local serever
import ApiError from './ApiError.js';



//from personal server to cloudinary
const uploadOnCloudinary = async(filePath)=>{
    try{
        cloudinary.config({ 
            cloud_name: process.env.CLOUDINARY_NAME, 
            api_key: process.env.CLOUDINARY_API_KEY, 
            api_secret: process.env.CLOUDINARY_API_SECRET
        });
        if(!filePath){
            throw new ApiError(502,"Upload on Cloudinary failed as filePath not found!!")
        }
        const stats = fs.statSync(filePath)
        console.log("Size:", stats.size)
        const response = await cloudinary.uploader
        .upload(filePath,{
            resource_type: "auto"
        })
        console.log("File has been uploaded successfully!!",response.url)
        fs.unlink(filePath, (err) => {
        if (err) {
            console.error('Error deleting file:', err);
            return;
        }
        console.log(`${filePath} was successfully deleted.`);
        });

        return response;
    }
    catch(error){
        console.log(`Upload on Cloudinary Failed!!}`,error)
        fs.unlink(filePath, (err) => {
        if (err) {
            console.error('Error deleting file:', err);
            return;
        }
        console.log(`${filePath} was successfully deleted.`);
        });//remove locally saved file as the file operation got failed
        return null;
    }
}

// uploadOnCloudinary("node_pipeline/public/tmp/Flux_Dev_Closeup_anime_portrait_of_a_male_humanoid_character_w_3.jpg")

export default uploadOnCloudinary
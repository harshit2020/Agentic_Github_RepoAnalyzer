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
        console.log(`Upload on Cloudinary Failed!! \n${error}`)
        fs.unlink(filePath)//remove locally saved file as the file operation got failed
        return null;
    }
}


export default uploadOnCloudinary
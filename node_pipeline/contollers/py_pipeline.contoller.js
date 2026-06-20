import asyncHandler from '../utils/asyncHandler.js'
import ApiError from '../utils/ApiError.js';
import axios from "axios";

const get_user_setup = asyncHandler(async(req, res) => {
    try{
        const {user_id} = req.query
        console.log(user_id)
        const url = process.env.FASTAPI_INTERNAL_URL+"/api/v1/user_setup"
        const response = await axios.get(url, {
            params: { user_id: user_id } 
        });
        console.log(response.data)
        return res.json(response.data)
    }
    catch(error){
        throw new ApiError(500,`User fetching failed \n ${error}`)
    }
})

const get_model_names = asyncHandler(async(req, res) => {
    try{
        const url = process.env.FASTAPI_INTERNAL_URL+"/api/v1/models/getModelNames"
        const response = await axios.get(url)
        console.log(response.data)
        return res.json(response.data)
    }
    catch(error){
        throw new ApiError(500,`Model List fetching failed \n ${error}`)
    }
})

const get_indexed_repos = asyncHandler(async(req,res)=>{
    try{
        const {user_id} = req.query
        const url = process.env.FASTAPI_INTERNAL_URL+"/api/v1/user_indexed_repos"
        const response = await axios.get(url,{
            params:{
                user_id
            }
        })
        console.log(response.data)
        return res.json(response.data)
    }
    catch(error){
        throw new ApiError(500,`Failed to get indexed repos as ${error}`)
    }
})

export{
    get_user_setup,
    get_model_names,
    get_indexed_repos
}
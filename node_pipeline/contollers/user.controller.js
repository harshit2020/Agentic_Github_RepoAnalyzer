import asyncHandler from "../utils/asyncHandler.js"
import ApiError from "../utils/ApiError.js";
import User from "../models/user.model.js";
import ApiResponse from "../utils/ApiResponse.js";
import uploadOnCloudinary from "../utils/cloudinary.js"

const generateAccessAndRefreshToken = async(user)=>{
    try{
        const accessToken = user.generateAccessToken()
        const refreshToken = user.generateRefreshToken()
        user.refreshToken = refreshToken
        await user.save({ validateBeforeSave:false })
        return {accessToken,refreshToken}
    }
    catch(error){
        throw new ApiError(500,`Something went wrong while generating Access and Refresh Tokens\n ${error}`)
    }
}

const registerUser = asyncHandler(async(req,res)=>{
    let propss_check = true;
   
    const{email,username,password} = req.body
   0 //Validation
  
   const propss = [email,username,password]
    for(let i=0;i<3;i++){
        console.log(propss[i])
        if(propss[i]!=""){
            continue
        }
        propss_check=false
    }
    if(!propss_check){
        throw new ApiError(400,"All fields are required!!!")
    }
    
    //check if user exists
    const existedUser = await User.findOne({
        $or:[{username},{email}]
    })
    
    if(existedUser){
        throw new ApiError(409,"User already exists!!!")
    }
   
    //cheack images
    
    const avatarPath = req.files?.avatar[0]?.path
     let coverImagePath;
    if(req.files&&Array.isArray(req.files.coverImage)&&req.files.coverImage.length>0){
        coverImagePath = req.files.coverImage[0].path
    }
    // if(!avatarPath){
    //     throw new ApiError("400","Avatar is necessary!!!")
    // }
    //upload to cloudinart
    const avatarOnCloudinary = await uploadOnCloudinary(avatarPath)

    //validate image
    if(!avatarOnCloudinary){
        throw new ApiError(400,"Avatar File is required")
    }
    //create user object
    const user = await User.create({
        avatar:avatarOnCloudinary.url,
        email:email,
        password:password,
        username:username.toLowerCase()
    })
    console.log(user._id)
    //check if user is created
    const userCreated = await User.findById(user._id).
    select(
        "-password -refreshToken"
    )

    if(!userCreated){
        throw new ApiError(500,"Error registering user!!")
    }

    //send response
    return res.status(200).json(
        new ApiResponse(201,userCreated,"Registered User successfully!!")
    )

})

const loginUser = asyncHandler(async(req,res)=>{
    console.log("Inside login user")
    const{email,username,password} = req.body
    //check if username and pwd is given or not
    if(!(username||password)){
        throw  new ApiError(401,"Username or password is incorrect")
    }

    //check if username exist in DB
    const userExists = await User.findOne({
        $or:[{username},{email}]
    })
    if(!userExists){
        throw new ApiError(403,"User not found")
    }

    //check for password
    const checkPwd = await userExists.isPasswordCorrect(password)
    if(!checkPwd){
        throw new ApiError(410,"Credential does not match existing user!!")
    }
     
    //generate tokens
    const {accessToken,refreshToken} = await generateAccessAndRefreshToken(userExists)
    

    //cookies
    const options = {
        Http:true,
        secure:true
    }

    return res
    .status(201)

    .json(
        new ApiResponse(200,{userExists:username},"User Login successful")
    )
})

// const logoutUser = asyncHandler(async(req,res)=>{
//     await User.findByIdAndUpdate(req.user._id,
//         {
//             $set:{
//                 refreshToken:undefined
//             }
//         },
//         {new:true}
//     )

//     const options = {
//         Http:true,
//         secure:true
//     }

//     return res
//     .status(201)
//     .clearCookie("accessToken",options)
//     .clearCookie("refreshToken",options)
//     .json(
//         new ApiResponse(200,{},"Logout Successful")
//     )
// })

const changeCurrentPassword = asyncHandler(async(req,res)=>{
    const {current_password,new_password,user_id} = req.body
    const user = await User.findOne({email:user_id})
    if(!user){
        throw new ApiError(401,"User not found")
    }
    const passwordCheck = await user.isPasswordCorrect(current_password)
    if(!passwordCheck){
        throw new ApiError(405,"Password Incorrect")
    }
    user.password = new_password
    await user.save({validateBeforeSave:false})

    return res
    .status(200)
    .json(
        new ApiResponse(201,{},"Password Changed Successfully!!!")
    )
})



export {
    registerUser,
    loginUser,
    changeCurrentPassword,
}
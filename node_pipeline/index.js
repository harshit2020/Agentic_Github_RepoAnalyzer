import app from "./app.js";
import dotenv from 'dotenv';
import worker from "./queue/worker.js"
import connectDB from "./utils/connectMongoDB.js";
dotenv.config({ path: './node_pipeline/.env' })

try{
    app.listen(process.env.NODE_APP_PORT)
    console.log(`Server is running at port: ${process.env.NODE_APP_PORT}`)
    connectDB()
    console.log(process.env.CLOUDINARY_NAME)
    console.log(process.env.CLOUDINARY_API_KEY)
    console.log(process.env.CLOUDINARY_API_SECRET)
}
catch(e){
    console.log(`APP Failed to start \n ${e}`)
}
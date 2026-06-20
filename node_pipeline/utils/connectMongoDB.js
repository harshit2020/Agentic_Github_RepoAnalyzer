import mongoose from 'mongoose';


export default async function connectDB() {
    try{
        await mongoose.connect(`${process.env.MONGO_DB_HOST}:${process.env.MONGO_DB_PORT}/${process.env.MONGO_DB_COLLECTION}`);
        console.log("Connected to MongoDB")
    }
    catch(e){
        throw new Error(`Connection to mongoDB failed!! \n ${e}`)
    }
  
}

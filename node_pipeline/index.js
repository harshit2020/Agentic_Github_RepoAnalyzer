import app from "./app.js";
import dotenv from 'dotenv';
import worker from "./queue/worker.js"

dotenv.config({ path: './node_pipeline/.env' })

try{
    app.listen(process.env.NODE_APP_PORT)
    console.log(`Server is running at port: ${process.env.NODE_APP_PORT}`)
}
catch(e){
    console.log(`APP Failed to start \n ${e}`)
}
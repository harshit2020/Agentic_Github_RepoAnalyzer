
const redis_connection =  
        {  
            connection: {
                            host: process.env.REDIS_HOST,
                            port: process.env.REDIS_PORT,
                        }
        }

export default redis_connection
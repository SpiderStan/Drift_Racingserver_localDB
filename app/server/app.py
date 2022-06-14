from fastapi import FastAPI

from .routes.driftapi import router as DriftapiRouter

app = FastAPI()

app.include_router(DriftapiRouter, tags=["Driftapi"], prefix="/driftapi")
	
@app.get("/", tags=["racingserver_api"], description="Entry endpoint that directs to the openapi docs.")
async def read_root():
    return {"message": "Welcome to the Sturmkind Dr!ft Community API & Reference Racing Server API. To see the available api calls, visit /docs."}

import os


from ingestion_pipeline import create_retreiver


def get_retreived_docs(query="ML algorithms train on datasets",k=3):
    retreiver=create_retreiver(k=5)
    res=retreiver.invoke(query)
    return res







    
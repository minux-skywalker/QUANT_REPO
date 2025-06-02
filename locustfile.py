from locust import HttpUser, task

class ResumeMatcherUser(HttpUser):
    @task
    def upload_jd_and_resumes(self):
        with open("jd.txt", "rb") as jd, \
             open("Jane Smith_Resume_F.docx", "rb") as r1, \
             open("John Doe_Resume _5.docx", "rb") as r2:

            files = [
                ("jd", ("jd.txt", jd, "text/plain")),
                ("resumes", ("resume1.docx", r1, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
                ("resumes", ("resume2.docx", r2, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
            ]

            self.client.post("/upload", files=files)

from django.test import TestCase
from upload.models import UploadedFile, UploadedFileSerializer


class ConventionModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        UploadedFile.objects.create(
            filename="image.png",
            filepath="/path/to/file",
            size=12345,
            content_type="image/png",
            thumbnail=(
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAYAAAA"
                + "5ZDbSAAAAAXNSR0IArs4c6QAACJ1JREFUeF7tnX1MVWUcx7+XlwvCLl5QQI"
                + "0QDEh8WQxWJhMXBGZNnRr/iEmzuUVW5uZWppJrutlcyyRntWq5NeGf3FDbN"
                + "DWZbY6sKAmF4sUrZCSIdBGkC9wL7XmO98ybgg/3Xj33Oed3/rn3Oed5/X1+"
                + "L+d57j3PMQ04+kdAh24lYCLAumXLB0aA9c2XAOucLwH2B+Co8M/8Uc19qYN"
                + "ctB/ESoD9IMRAroIABzIdP/SNAPtBiIFcBQEOZDp+6BsB9oMQA7mK8QI+d3"
                + "61x3BeWvMtLtZ1iQ3RBEREhqK/bwiJ0y1oa+3l5WakWGFr6cHIiOfCJN1F3"
                + "0OsLpcLwcHBY+YaL+D/VxYbH4FrHf0ep9PnxiJ9ziSUly9CUdEJnPjmEvp6"
                + "B3HT+ToiQz7iefMKEnH6ZBv/fvL7QhQs/PqOfhLgu6Cz2+2wWq38Snl5BYq"
                + "KVvkdsGNkA4aHRxARrMAa7WD5wk1l/PLf3S+jq8uBNUXHcf7nDhVw7+Br/H"
                + "xa8pdotK1F8rTPef7fbWtpoYMJ4pnFz2H9KyWYOXMmSt/ZjpCQEJQf/Arnf"
                + "vwJ8554HE/nL8LCnAUoWFSAJ+fNQ1BQEBdgZ2cn4uLi4I0Fh4QEYdrDFrTZ"
                + "eoQAP7c8Bde7/+V5z5x5nkNnFpyTm4jjx23q+ZioT+AcdCFt1iRc+LWTAA8"
                + "ODmLFykLF5eU+heTkZKxcuYKnGdgXXyxG8ZoXeDq/4Bnk5eViy9ub4XQ6uS"
                + "Kw40EAzluchNPHL3soAwP8RPY0vPfuDx7nexyvIijIBIt5HwEeHh7G+fO1y"
                + "Mh4DL29vdi8eQv279/Hv0dFRaGm5hekpDyCgYEBXLh4EZWVh1G290Pk5uWj"
                + "6vQprwGPaba3XbzdRTe2roXVGoaKiia8UfKd6qI7e0pgNgfhrTer8elHv6J"
                + "0Zzba/+rDFx//RoCZLBlkdjMVGhrKRetyDWPxs8/i5IlveXpoaIjfaLldM4"
                + "NvsVhUDN5YsChgX/PRTdYoEuzo6EB8fLyQfAmwkJjkzUSA5WUn1HMCLCQme"
                + "TMRYHnZCfX86BHP6YtQoQeUiW6yHpCgtWrGZLfbdfe32QnhZq3kGXDt6hIw"
                + "kzJBVnSNAN+yOYdjAE3NLXz5kS1DsiMrK4t/1tTUjJpmS511dXXq9a6uLrS"
                + "2tqppm82G7u5uNV1bW+tRv7tud3v+ThNgACGhZly6ZONwp0+fDpPJFHCu1t"
                + "sOEWAAjU0tmDNnjrcyDOhyhgf855W/YLf3qO44oGl50TnDA667UO8RX72QY"
                + "UAXMTxgc9iEgAbka+cMD5gs2FcV0qi86DyYAGsEyNdmCTAtdHAJUAz21ZQ0"
                + "Kk8WTBbMJUAxWCML9LVZsmCyYIrBvlqRluXJgsmCKQZraYG+ti1qwRcuNvC"
                + "mMjMzfW0yIMsbfqmS5sEBqZf37pSoBdM06d6yDMgcBJhusrgELtmU/0+xZ4"
                + "P1eFAMpt+D5dRrctHkomkeLKftKr0WteCrHdd4/sTERJmHO2rfKQZTDJZTs"
                + "UUtmObBcvIVdtFaAWaPs6xevZpPz/bs2cOl3NDQwPcLSUlJQVhYmF8kb3gX"
                + "faP3Jhfk5MmT/SJQkUrYJi4HDx5ESUkJz15UVITy8nIOOD09XaQK4TyGB6z"
                + "FWnRubi6qqqrugMQAs2ejIiIicOzYMf6sVGpqKlatWoXq6mosW7YMR44cQX"
                + "19PWbNmoUNGzZg7969OHz4MJYsWYKmpiZe57p163D27Fn+3fCAtXDRS5cux"
                + "dGjR8cEPH/+fA6VHe7v/wfMzpvNyrPQu3btQnZ2NvLz83HqlLJ/FwHW6D9Z"
                + "bEfYwsJCHDp0iMfcnJwcbnG3W/C2bduwY8cO/qSjG7D7c+fOnWDXly9fjsr"
                + "KSg6SbdS2detW7N69W93PiwAD6P5H2StyypQpwnHNXxkrKiowd+7cUZ9svH"
                + "LlCtjzx+xmzG3NBw4cQHFxsQqxubkZV69exYIFC+7aLcO7aC1i8HgV5HZ3P"
                + "d6yhgesRQweLyRf8hNgenzUF/3RrqzoStbNfgfvZHR0tHadvY8tG96CZYjB"
                + "vvA3PGCKwb6oj4ZlRV00AdYQki9NiwJ2upSN/tjyoB4Pw7toU5Dy3gX3bu9"
                + "6g2x4wOSiJVVpURdNgHUOODhE+TXmXm83k1QM9HPhkHOYs4uMjJSV4Zj9ph"
                + "hMS5VyKjbFYIWb4S2YlirlNGDhf1X23VRe+BgTEyPpSMfutuEtmKZJkuo1x"
                + "WCKwVwCFIN1bsHXu+18hFOnTpV0pBSDx5QAxWBJ9ZpiMMVgisGSGi/vtqgF"
                + "t//dwfMnJSXJPNxR+07zYFqLllOxRS2YbrLk5CvsomkerHPAl1v/5CNMS0u"
                + "TdKQ0D6Z5sB5Vl2IwzYNpHiyzZYta8B+NzXyY7EFsPR40D6Z5sJx6LWrBNA"
                + "+Wky/Ng29xIxdNLlpOEyYXTdMkLgGKwXIaMMVgisGKBMiCdW7BBJgASyoBu"
                + "smitWiZVZemSWTBdJNFFiyzBMiCKQbLrL8Ug8mCKQYbwYLrG36HyzWMrKws"
                + "mYc7at8N/3Mhe+lFqDlcl3DZoAwP2L0ezTZCy8jI0B1o3QEuKyvDxo0bEWZ"
                + "WNhkVPdiaNAPc2dmJ9vZ2Xoy5bfaqm/7+fjVdW1sLp9OppmtqatQmWH7RNP"
                + "McmZmZav7w8HDMnj1bTU+cOJG/4s5dX2xsLH9DqjvNdqifMWOGmk5ISEB8f"
                + "LyaZn/kZzvo6gowg7tp0yb09fXBOtEiylbNx4R+7dp13Oi9wc+lpT2KtrZW"
                + "OBzKtv8s3dLSDJfLpaYbG/9Qy7PromnWVmpqmpqfveAqKSlZTbOd9x56KEF"
                + "NW61WxMXFq2mLJYrvSuBujylAdHSMmk5IeBhMaXQDmL35q7S0FNu3b+efot"
                + "OkcWuBZAVM69evV3bE1tmx54P3dTYi74ZjGnD06xKwd+LQXykCrD+mHiMiw"
                + "ARY5xLQ+fDIgnUO+D8ei8UeY8TTjQAAAABJRU5ErkJggg=="
            ),
        )

    def test_object_str(self):
        uploaded_file = UploadedFile.objects.first()
        expected_object_name = f"{uploaded_file.filename}"
        self.assertEqual(str(uploaded_file), expected_object_name)

    def test_serialise(self):
        uploaded_file = UploadedFile.objects.first()
        expected_object = {
            "id": uploaded_file.id,
            "uuid": str(uploaded_file.uuid),
            "filename": uploaded_file.filename,
            "filepath": uploaded_file.filepath,
            "size": uploaded_file.size,
            "content_type": uploaded_file.content_type,
            "thumbnail": uploaded_file.thumbnail,
        }
        self.assertEqual(UploadedFileSerializer(uploaded_file).data, expected_object)

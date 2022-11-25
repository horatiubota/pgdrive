
This package provides a simple interface to Google Drive API v3. It allows you to read and write Google Drive files to and from pandas DataFrames.

Needs a GCP IAM Service account to work. See https://cloud.google.com/iam/docs/creating-managing-service-accounts for more information. Ask your Cloud Admin to create a service account for you and provide you with a JSON key.


# Installation

```
pip install git+https://github.com/horatiubota/pgdrive
```

You need to set the Google Drive service account JSON key as an environment variable called `GOOGLE_DRIVE_CREDENTIALS`. You can do this by running the following command in your terminal:

```
export GOOGLE_DRIVE_CREDENTIALS='content of your JSON key'
```

or if you are using `conda` to manage your environment:

```
 conda env config vars set GOOGLE_DRIVE_CREDENTIALS='content of your JSON key'
```

# Usage

Make sure the files you want to read or write are shared with the service account. You can share a file with the service account by going to the file's sharing settings on the Google Drive web app and adding the service account's email address as a collaborator. If you want to share multiple files, you can share an entire folder or drive with the service account.


```
import pgdrive

# read a file by url copied from the browsers address bar
pgdrive.read_drive("https://docs.google.com/file/d/<fileid>")
pgdrive.read_drive("https://docs.google.com/spreadsheets/d/<fileid>")

# read a file by path
pgdrive.read_drive(path="drive_name/folder1/folder2/file.csv")

# pass additional arguments to pandas.read_csv or pandas.read_excel
pgdrive.read_drive(path="drive_name/folder1/folder2/file.xlsx", sheet_name="Sheet1")

# write a DataFrame to a Drive path
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.pipe(pgdrive.to_drive, path="drive_name/folder1/folder2/file.csv")

# overwriting files raises an exception, you can disable this with:
df.pipe(pgdrive.to_drive, path="drive_name/folder1/folder2/file.csv", overwrite=True)

# upload local file to drive path
pgdrive.upload_file("local_file.csv", "drive_name/folder1/folder2/file.csv")
```

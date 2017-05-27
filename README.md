This is a project management webapp running on Google App Engine

## Installing and setup on Ubuntu
1. Follow [these instructions](https://cloud.google.com/sdk/docs/#deb)
1. Install this package: `google-cloud-sdk-app-engine-python`
2. `bower install`
2. `gcloud init`


## Local Devserver
To run use `dev_appserver.py .` in project root.
* App is available on http://localhost:8080/
* Local Admin interface http://localhost:8000/instances

You can also clear datastore at start: `dev_appserver.py --clear_datastore=yes app.yaml`

To drop into local debugger, add `import pdb; pdb.set_trace()` to set a breakpoint.
This invokes the [Python debugger](https://docs.python.org/3/library/pdb.html)

## `glcoud` commands
* Deploy:  `gcloud app deploy`. **ENSURE THAT INDEXES ARE UP TO DATE!**
* List projects: `gcloud projects list`
* Change project project: `gcloud init`

If indexes changed, do this: `gcloud datastore create-indexes index.yaml`, otherwise things get borked

## Installing Python packages
New packages are installed to the `lib` folder using the `pip install -t lib <package-name>` command.

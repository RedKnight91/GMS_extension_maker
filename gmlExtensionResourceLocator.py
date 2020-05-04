import utilities as utils
import gmsUtilities as gms
import os


def locateInternalScripts(workPaths):
	viewPath = os.path.join('scripts', workPaths.internalGroupName)
	scripts = locateScripts(workPaths, viewPath)
	return scripts

def locateExternalScripts(workPaths):
	viewPath = os.path.join('scripts', workPaths.externalGroupName)
	scripts = locateScripts(workPaths, viewPath)
	return scripts

def locateScripts(workPaths, viewPath):
	scripts = locateResourceType(workPaths, 'GMScript', 'ResourceTree_Scripts', viewPath)
	return scripts

def locateObjects(workPaths):
	objects = locateResourceType(workPaths, 'GMObject', 'ResourceTree_Objects', 'objects')
	return objects

def locateExtensions(workPaths):
	extensions = locateResourceType(workPaths, 'GMExtension', 'ResourceTree_Extensions', 'extensions')
	return extensions



def isViewUuid(viewsDir, uuid):
	viewPath = utils.makePath(viewsDir, uuid, 'yy')
	return os.path.exists(viewPath)

def findResourcePaths(sourceProjectDir, projectJson, uuids):
	projectResources = projectJson['resources']
	resources = utils.findDictsWithKeyValueInList(projectResources, 'Key', uuids)

	dir = sourceProjectDir
	resourcePaths = [gms.makeResourceDirPath(dir, resource['Value']['resourcePath']) for resource in resources]

	return resourcePaths

def makeViewPaths(viewsDir, uuids):
	viewPaths = [os.path.join(viewsDir, uuid) + '.yy' for uuid in uuids ]
	viewPaths = [path for path in viewPaths if os.path.exists(path)]
	return viewPaths

def filterViewByName(viewPaths, name):
	view = next((view for view in viewPaths if (utils.readJson(view)['folderName'] == name)), None)
	assert view != None, 'No matching view found'

	return view

#Gets a viewPath given a Group path like 'scripts/Name/things'
def getViewAtPath(rootView, viewsDir, viewPath):
	viewPath = utils.splitPath(viewPath)
	currentViewPath = rootView
	currentViewJson = utils.readJson(currentViewPath)
	path = [currentViewJson['folderName']]

	while (path != viewPath):
		viewChildPaths = makeViewPaths(viewsDir, currentViewJson['children'])
		nextView = viewPath[len(path)]

		currentViewPath = filterViewByName(viewChildPaths, nextView)
		currentViewJson = utils.readJson(currentViewPath)

		path.append(currentViewJson['folderName'])
		
	return currentViewPath

def getViewResourcesRecursive(viewsDir, viewJson):
	childViews = [uuid for uuid in viewJson['children'] if isViewUuid(viewsDir, uuid)]
	resources = [uuid for uuid in viewJson['children'] if uuid not in childViews]

	childViewPaths = utils.makePathList(viewsDir, childViews, 'yy')

	for view in childViewPaths:
		childViewJson = utils.readJson(view)
		childViewResources = getViewResourcesRecursive(viewsDir, childViewJson)
		resources.extend(childViewResources)

	return resources

def getViewResources(project, viewPath):
	sourceProjectJson = utils.readJson(project.file)
	viewJson = utils.readJson(viewPath)

	resourceUuids = [] if ('children' not in viewJson) else getViewResourcesRecursive(project.viewsDir, viewJson)
	resourcePaths = findResourcePaths(project.dir, sourceProjectJson, resourceUuids)
	return resourcePaths



def locateResourceType(workPaths, filterType, resourceType, viewPath):
	print('\nLOCATING RESOURCES\n')

	project = workPaths.sourceProject
	viewsDir = project.viewsDir

	rootView = gms.getRootResourceView(project, filterType, resourceType)

	viewAtPath = getViewAtPath(rootView,viewsDir, viewPath)
	resources = getViewResources(project, viewAtPath)

	print('\nRESOURCES LOCATED\n')

	return resources
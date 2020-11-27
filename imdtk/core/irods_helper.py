#
# Helper class for iRods commands: manipulate the filesystem, including metadata.
#   Written by: Tom Hicks. 10/15/20.
#   Last Modified: Remove unused is_connected method.
#
import os
import errno
import pathlib as pl

from irods.session import iRODSSession
from irods.collection import iRODSCollection
from irods.data_object import iRODSDataObject

from config.settings import DEFAULT_IRODS_ENV_FILENAME, DEFAULT_IRODS_ENV_FILEPATH
from config.settings import DEFAULT_IRODS_AUTH_FILENAME, DEFAULT_IRODS_AUTH_FILEPATH
from imdtk.core import Metadatum


class IRodsHelper:
    """ Helper class for iRods commands """

    @staticmethod
    def cleanup_session (session):
        """ Cleanup the given session. """
        if (session):
            session.cleanup()


    @staticmethod
    def to_dirpath (dir_path):
        """ Add a trailing slash to the given directory path to mark it is an iRods
            directory path. This is required by the 'put' command, for example. """
        if (str(dir_path).endswith("/")):
            return str(dir_path)
        else:
            return "{}/".format(dir_path)


    def __init__ (self, args={}, connect=True):
        self.args = args                    # save arguments passed to this instance
        self._DEBUG = args.get('debug', False)
        self._cwdpath = None                # current working directory - a PurePath
        self._root = None                   # root directory path - a PurePath
        self._session = None                # current session - None until connected
        if (connect):                       # connect now unless specified otherwise
            self.connect()


    def __enter__ (self):
        return self


    def __exit__ (self, exc_type, exc_value, traceback):
        self.cleanup()


    def cleanup (self):
        """ Cleanup the current session. """
        self.disconnect()


    def connect (self):
        """ Open and remember an iRods session using the instantiation arguments. """
        if (self._DEBUG):
            print("(IRodsHelper.connect): args={}".format(self.args))

        self._session = self.make_session()

        if (self._DEBUG):
            print("(IRodsHelper.connect): SESSION={}".format(self._session))

        # users root directory is set to their iRods home directory
        self.set_root()


    def cd_down (self, subdir):
        """ Change the current working directory to the given subdirectory. """
        if (self._cwdpath):
            self._cwdpath = self._cwdpath / subdir  # NB: maintain PurePath


    def cd_root (self):
        """ Reset the current working directory to the users root directory. """
        if (self._root):
            self._cwdpath = pl.PurePath(self._root)
        else:
            self._cwdpath = None


    def cd_up (self):
        """ Change the current working directory to the parent directory. """
        if (self._cwdpath and self._root):  # if connected
            parent = self._cwdpath.parent
            if (parent >= self._root):      # cd must not rise above root dir
                self._cwdpath = parent
        else:
            self._cwdpath = None


    def cd (self, dir_path, absolute=False):
        """ Change the current working directory to the given path relative to the
            current working directory (default) OR relative to the users root directory,
            if the absolute argument is True.
        """
        if (self._cwdpath and self._root):  # if connected
            if (absolute):                  # path is relative to root dir
                newdir = pl.PurePath(self._root / dir_path)
            else:                           # path is relative to current working dir
                newdir = pl.PurePath(self._cwdpath / dir_path)
            if (newdir >= self._root):      # cd must not rise above root dir
                self._cwdpath = newdir
        else:
            self._cwdpath = None


    def collection_exists (self, apath):
        """ Tell whether the given path points to an existing iRods collection (dir) or not. """
        if (apath):                         # sanity check
            return (self._session.collections.exists(apath))
        else:
            return False


    def cwd (self):
        """ Return the current working directory path as a string. """
        return str(self._cwdpath)


    def cwd_rel_path (self, path):
        """ Return an iRods path for the given path relative to the current working directory. """
        return str(self._cwdpath / path)


    def delete_dir (self, dir_path, absolute=False, force=False, recurse=True):
        """ Delete the specified directory relative to the iRods current working directory
            (default) OR relative to the users root directory, if the absolute argument is True.
        """
        try:
            dirobj = self.getc(dir_path, absolute=absolute)
            dirobj.remove(force=force, recurse=recurse)
            return True
        except:                             # ignore any errors
            return False


    def delete_file (self, file_path, absolute=False):
        """ Delete the specified file relative to the iRods current working directory (default)
            OR relative to the users root directory, if the absolute argument is True.
        """
        try:
            obj = self.getf(file_path, absolute=absolute)
            obj.unlink(force=True)
            return True
        except:                             # ignore any errors
            return False


    def disconnect (self):
        """ Close down and cleanup the current session. """
        if (self._session):
            self._session.cleanup()
            self._session = None
            self._cwdpath = None
            self._root = None
            self.args = {}


    def file_exists (self, apath):
        """ Tell whether the given path points to an existing iRods file or not. """
        if (apath):                         # sanity check
            return (self._session.data_objects.exists(apath))
        else:
            return False


    def gen_file_paths (self, root_dir, topdown=True):
        """
        Generator to yield all absolute iRods file paths in the directory tree under the
        given root directory.
        """
        for root, dirs, files in self.walk(root_dir, topdown=topdown):
            for fyl in files:
                yield fyl.path


    def get_authentication_file (self, args):
        """
        Return a path to the iRods authentication file read from the given arguments, or
        OR a path specified by the environment variable IRODS_AUTHENTICATION_FILE,
        OR a default path specified in the app configuration,
        OR raise a custom FileNotFoundError if no authentication file is specified.
        """
        try:
            auth_file = args["irods_authentication_file"]
        except KeyError:
            try:
                auth_file = os.environ["IRODS_AUTHENTICATION_FILE"]
            except KeyError:
                auth_file = DEFAULT_IRODS_AUTH_FILEPATH
                if (not auth_file):
                    # raise a custom FileNotFound error:
                    errMsg("No iRods authentication file specified.")
                    raise OSError(errno.ENOENT, errMsg, DEFAULT_IRODS_AUTH_FILENAME)

        if (self._DEBUG):
            print("(IRodsHelper.get_authentication_file): auth_file={}".format(auth_file))

        return auth_file                    # return the filepath


    def getc (self, dir_path, absolute=False, rootrel=False):
        """
        Get the collection (directory) at the specified path, which is interpreted
        based on the given absolute/relative flags.

        :raises irods.exception.CollectionDoesNotExist if collection (dir) not found or not readable.
        """
        dirpath = self.path_to(dir_path, absolute, rootrel)
        return self._session.collections.get(dirpath)


    def get_cwd (self):
        """ Get directory information for the current working directory. """
        return self._session.collections.get(self._cwdpath) if (self._cwdpath) else None


    def get_environment_file (self, args):
        """
        Return a path to the iRods environment file read from the given arguments, or
        OR a path specified by the environment variable IRODS_ENVIRONMENT_FILE,
        OR a default path specified in the app configuration,
        OR raise a custom FileNotFoundError if no environment file is specified.
        """
        try:
            env_file = args["irods_env_file"]
        except KeyError:
            try:
                env_file = os.environ["IRODS_ENVIRONMENT_FILE"]
            except KeyError:
                env_file = DEFAULT_IRODS_ENV_FILEPATH
                if (not env_file):
                    # raise a custom FileNotFound error:
                    errMsg("No iRods environment file specified.")
                    raise OSError(errno.ENOENT, errMsg, DEFAULT_IRODS_ENV_FILENAME)

        if (self._DEBUG):
            print("(IRodsHelper.get_environment_file): env_file={}".format(env_file))

        return env_file                     # return the filepath


    def getf (self, file_path, absolute=False, rootrel=False):
        """ Get the file at the specified file path, which is interpreted based on
            the given absolute/relative flags.

        :raises irods.exception.DataObjectDoesNotExist if file not found or not readable
        """
        filepath = self.path_to(file_path, absolute, rootrel)
        return self._session.data_objects.get(filepath)


    def get_metac (self, dir_path, absolute=False):
        """ Get the metadata for the specified directory relative to the iRods
            current working directory (default) OR relative to the users root directory,
            if the absolute argument is True.
        """
        dirobj = self.getc(dir_path, absolute=absolute)
        return [Metadatum(item.name, item.value) for item in dirobj.metadata.items()]


    def get_metaf (self, file_path, absolute=False):
        """ Get the metadata for the specified file relative to the iRods
            current working directory (default) OR relative to the users root directory,
            if the absolute argument is True.
        """
        obj = self.getf(file_path, absolute=absolute)
        return [Metadatum(item.name, item.value) for item in obj.metadata.items()]


    def get_root (self):
        """ Get directory information for the users root directory. """
        return self._session.collections.get(self._root)


    def is_collection (self, node):
        """ Tell whether the given iRods node is a collection or not. """
        return isinstance(node, iRODSCollection)


    def is_dataobject (self, node):
        """ Tell whether the given iRods node is a file or not. """
        return isinstance(node, iRODSDataObject)


    def make_session (self):
        """
        Create and return an iRods session using the given arguments dictionary.

        :raises: a custom FileNotFoundError if the environment or authentication
                 filepaths are not provided in the arguments, the environment,
                 or in an imported default application variable.
        """
        env_file = self.get_environment_file(self.args)
        auth_file = self.get_authentication_file(self.args)
        return iRODSSession(irods_authentication_file=auth_file, irods_env_file=env_file)


    def mkdir (self, dir_path, absolute=False):
        """ Make a directory (collection) with the given path relative to the iRods
            current working directory (default) OR relative to the users root directory,
            if the absolute argument is True. Returns the iRods ID of the collection.
        """
        if (absolute):
            dirpath = self.abs_path(dir_path)  # path is relative to root dir
        else:
            dirpath = self.rel_path(dir_path)  # path is relative to current working dir
        return self._session.collections.create(dirpath)


    def path_to (self, apath, absolute=False, rootrel=False):
        """
        Interpret the given path using the values of the absolute and rootrel flags.
        If absolute is True, return the path unchanged. If rootrel is True,
        return an absolute path calculated relative to the user's root directory,
        else return an absolute path calculated relative to the current working directory.
        """
        if (absolute):                            # if path is absolute
            return apath                          # then return it w/o change
        elif (rootrel):                           # else if path is relative to user root dir
            return self.root_rel_path(apath)      # expand to full path
        else:                                     # else path is relative to current directory
            return self.cwd_rel_path(apath)       # expand to full path


    def put_file (self, local_file, file_path, absolute=False):
        """ Upload the specified local file to the specified path, relative to the iRods
            current working directory (default) OR relative to the users root directory,
            if the absolute argument is True.
        """
        if (absolute):
            filepath = self.abs_path(file_path)  # path is relative to root dir
        else:
            filepath = self.rel_path(file_path)  # path is relative to current working dir
        self._session.data_objects.put(local_file, filepath)


    def put_metaf (self, metadata, file_path, absolute=False):
        """ Attach the given metadata on the file specified relative to the iRods
            current working directory (default) OR relative to the users root directory,
            if the absolute argument is True. Returns the new number of metadata items.
        """
        obj = self.getf(file_path, absolute=absolute)
        keys = [item.keyword for item in metadata]
        for key in keys:
            del(obj.metadata[key])
        for item in metadata:
            obj.metadata.add(item.keyword, item.value)
        return len(obj.metadata)


    def root (self):
        """ Return the user root directory as a string. """
        return str(self._root)


    def root_rel_path (self, path):
        """ Return an iRods path for the given path relative to the users root directory. """
        return str(self._root / path)


    def session (self):
        """ Return the current session object. """
        return self._session


    def set_connection (self, json_body):
        """ Create a session and set it as current, using the fields of the given JSON object. """
        self.disconnect()                   # close and cleanup any existing session
        self._session = iRODSSession(
            host=json_body["host"],
            port=json_body["port"],
            user=json_body["user"],
            password=json_body["password"],
            zone=json_body["zone"])
        self.set_root()                     # call with default arguments


    def set_root (self, home_dir="home", top_dir=""):
        """ Compute and set the users root directory to the users iRods home directory (default)
            OR to a subdirectory of the users home directory, specified by the 'top_dir' argument.
        """
        if (self._session):
            self._root = pl.PurePath("/", self._session.zone, home_dir, self._session.username, top_dir)
        else:
            self._root = None
        self.cd_root()                      # cd back to root after changing root dir


    def walk (self, root_dir=None, topdown=True):
        """
        Collection tree generator. For each subcollection in the root dir, yield a 3-tuple
        of (self, self.subcollections, self.data_objects). If no root dir is provided,
        then use the current directory.
        """
        root = self.get_cwd() if (root_dir is None) else root_dir
        yield from root.walk(topdown=topdown)

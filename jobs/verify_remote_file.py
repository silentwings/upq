# This file is part of the "upq" program used on springfiles.com to manage file
# uploads, mirror distribution etc. It is published under the GPLv3.
#
#Copyright (C) 2011 Daniel Troeder (daniel #at# admin-box #dot# com)
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
# Verify_remote_file: check the integrity of a file on a mirror by comparing
# the result of the PHP-script "deamon.php" with the stored hash in the DB
# 

#
# call this module with argument "<fmfid>"
#

import upqjob
import upqdb
import urllib

class Verify_remote_file(upqjob.UpqJob):

    where = ""

    def check(self):
        # TODO: check if time last file checked is < 1 Year
        self.enqueue_job()
        return True

    
    def run(self):
        # get files hash from DB
        fid=int(self.jobdata['fmfid'])
        result = upqdb.UpqDB().query("SELECT url_prefix, url_deamon, path, md5 FROM file_mirror_files AS f  LEFT JOIN file_mirror as m ON m.fmid=f.fmid WHERE fmfid=%d "%fid)
        res = result.first()

        if not res:
            self.msg = "File with jobdata='%s' not found in DB."%(self.jobdata)
            self.logger.debug(self.msg)
            return False

        script_url = res['url_prefix']+"/"+res['url_deamon']
        params     = urllib.urlencode({'p': res['path']})
        hash_url   = script_url+"?%s"%params

        # retrieve md5 hash from deamon.php on remote mirror server
        self.logger.debug("retrieving '%s'", hash_url)
        hash_file = urllib.urlopen(hash_url)
        hash = hash_file.read()

        self.msg = "received md5 hash for filename=%s on fmid=%s is %s" %(res['path'], fid, hash)
        self.result = hash
        self.logger.debug(self.msg)

        
        if res['md5'] == hash:
            self.msg = 'Remote hash matches hash in DB.'
            return True
        else:
			#TODO: delete from db to allow re-upload
            self.msg  = 'Remote hash does NOT match hash in DB.'
            return False

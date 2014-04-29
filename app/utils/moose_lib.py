from app.utils.log_helper import logger
from app.utils import mfs_exceptions
import socket
import struct
import time
import traceback
import sys

PROTO_BASE = 0

CLTOMA_CSERV_LIST = (PROTO_BASE+500)
MATOCL_CSERV_LIST = (PROTO_BASE+501)
CLTOCS_HDD_LIST_V1 = (PROTO_BASE+502)
CSTOCL_HDD_LIST_V1 = (PROTO_BASE+503)
CLTOMA_SESSION_LIST = (PROTO_BASE+508)
MATOCL_SESSION_LIST = (PROTO_BASE+509)
CLTOMA_INFO = (PROTO_BASE+510)
MATOCL_INFO = (PROTO_BASE+511)
CLTOMA_FSTEST_INFO = (PROTO_BASE+512)
MATOCL_FSTEST_INFO = (PROTO_BASE+513)
CLTOMA_CHUNKSTEST_INFO = (PROTO_BASE+514)
MATOCL_CHUNKSTEST_INFO = (PROTO_BASE+515)
CLTOMA_CHUNKS_MATRIX = (PROTO_BASE+516)
MATOCL_CHUNKS_MATRIX = (PROTO_BASE+517)
CLTOMA_QUOTA_INFO = (PROTO_BASE+518)
MATOCL_QUOTA_INFO = (PROTO_BASE+519)
CLTOMA_EXPORTS_INFO = (PROTO_BASE+520)
MATOCL_EXPORTS_INFO = (PROTO_BASE+521)
CLTOMA_MLOG_LIST = (PROTO_BASE+522)
MATOCL_MLOG_LIST = (PROTO_BASE+523)
CLTOMA_CSSERV_REMOVESERV = (PROTO_BASE+524)
MATOCL_CSSERV_REMOVESERV = (PROTO_BASE+525)
CLTOCS_HDD_LIST_V2 = (PROTO_BASE+600)
CSTOCL_HDD_LIST_V2 = (PROTO_BASE+601)

# PY3 compatibility, py3 range is same as py2k xrange
if sys.version_info >= (3, 0):
    xrange = range

class MooseFS():
    """
    MooseFS class based on mfscgi script for encapsulate moose data manipulating.

    """

    def __init__(self, masterhost='mfsmaster', masterport=9421):
        self.masterhost = masterhost
        self.masterport = int(masterport)
        self.masterversion = self.check_master_version()


    def bind_to_master(self):

        s = socket.socket()
        s.connect((self.masterhost, self.masterport))
        return s

    def mysend(self, socket, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = socket.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myrecv(self, socket, leng):
        msg = b''
        while len(msg) < leng:
            chunk = socket.recv(leng-len(msg))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            msg = msg + chunk
        return msg

    def check_master_version(self):
        masterversion = (0, 0, 0)
        s = self.bind_to_master()
        self.mysend(s, struct.pack(">LL", 510, 0))
        header = self.myrecv(s, 8)
        cmd, length = struct.unpack(">LL", header)
        data = self.myrecv(s, length)
        if cmd == 511:
            if length == 52:
                masterversion = (1, 4, 0)
            elif length == 60:
                masterversion = (1, 5, 0)
            elif length == 68 or length == 76:
                masterversion = struct.unpack(">HBB", data[:4])
        return masterversion


    def mfs_info(self, INmatrix=0):

        info = {
                'version':              None,
                'total_space':          None,
                'avail_space':          None,
                'trash_space':          None,
                'trash_files':          None,
                'reserved_space':       None,
                'reserved_files':       None,
                'all_fs_objects':       None,
                'directories':          None,
                'files':                None,
                'chunks':               None,
                'all_chunk_copies':     None,
                'regular_chunk_copies': None,
                'memusage':             None
            }

        try:
            s = self.bind_to_master()
            self.mysend(s, struct.pack(">LL", 510, 0))
            header = self.myrecv(s, 8)
            cmd, length = struct.unpack(">LL", header)
            data = self.myrecv(s, length)

            def info_helper(**kwargs):
                if len(kwargs) == 15:
                    kwargs.append({ 'version': ''.join([ kwargs['v1'], kwargs['v2'], kwargs['v3'] ]) })
                    for i in 'v1','v2','v3':
                        del kwargs[i]
                for i in kwargs:
                    info[i] = kwargs[i]
                return kwargs

            if length == 52:
                total, avail, trspace, trfiles, respace, refiles, nodes, chunks, \
                tdcopies = struct.unpack(">QQQLQLLLL", data)

                info =  info_helper(total_space=total, avail_space=avail,
                                      trash_space=trspace, reserved_files=refiles,
                                      trash_files=trfiles, reserved_space=respace,
                                      all_fs_objects=nodes, chunks=chunks,
                                      regular_chunk_copies=tdcopies)

            elif length == 60:
                total, avail, trspace, trfiles, respace, refiles, nodes, dirs, files, chunks, \
                tdcopies = struct.unpack(">QQQLQLLLLLL", data)

                info = info_helper(total_space=total, avail_space=avail, files=files,
                                     trash_space=trspace, trash_files=trfiles, reserved_space=respace,
                                     reserved_files=refiles, regular_chunk_copies=tdcopies,  directories=dirs,
                                     all_fs_objects=nodes, chunks=chunks)

            elif length == 68:
                v1, v2, v3, total, avail, trspace, trfiles, respace, refiles, nodes, dirs, files, chunks, \
                allcopies, tdcopies = struct.unpack(">HBBQQQLQLLLLLLL", data)

                info =  info_helper(total_space=total, avail_space=avail, files=files,
                                      version='.'.join([str(v1), str(v2), str(v3)]), trash_space=trspace,
                                      trash_files=trfiles, reserved_space=respace, reserved_files=refiles,
                                      all_fs_objects=nodes, chunks=chunks, regular_chunk_copies=tdcopies,
                                      directories=dirs, all_chunk_copies=allcopies)

            elif length == 76:
                v1, v2, v3, memusage, total, avail, trspace, trfiles, respace, refiles, nodes, dirs, files, \
                chunks, allcopies, tdcopies = struct.unpack(">HBBQQQQLQLLLLLLL", data)

                info =  info_helper(memusage=memusage, total_space=total, avail_space=avail,
                                      version='.'.join([str(v1), str(v2), str(v3)]), trash_space=trspace,
                                      trash_files=trfiles, reserved_space=respace, reserved_files=refiles,
                                      all_fs_objects=nodes, chunks=chunks, regular_chunk_copies=tdcopies,
                                      directories=dirs, all_chunk_copies=allcopies, files=files)

                s.close()

        except Exception:
            traceback.print_exc(file=sys.stdout)

        # All chunks state matrix
        matrix = []
        if self.masterversion >= (1, 5, 13):
            try:
                s = self.bind_to_master()
                if self.masterversion >= (1, 6, 10):
                    self.mysend(s, struct.pack(">LLB", 516, 1, INmatrix))
                else:
                    self.mysend(s, struct.pack(">LL", 516, 0))
                header = self.myrecv(s, 8)
                cmd, length = struct.unpack(">LL", header)
                if cmd == 517 and length == 484:
                    # This will generate a matrix of goals, from 0 to 10+
                    # for both rows and columns. It does not include totals.
                    for i in xrange(11):
                        data = self.myrecv(s, 44)
                        matrix.append(list(struct.unpack(">LLLLLLLLLLL", data)))
                s.close()
            except Exception:
                traceback.print_exc(file=sys.stdout)

        # Chunk operations info
        chunk_info = {}
        try:
            s = self.bind_to_master()
            self.mysend(s, struct.pack(">LL", 514, 0))
            header = self.myrecv(s, 8)
            cmd, length = struct.unpack(">LL", header)
            if cmd == 515 and length == 52 or length == 76:
                data = self.myrecv(s, length)
                loopstart, loopend, del_invalid, ndel_invalid, del_unused, ndel_unused, del_dclean, ndel_dclean, \
                del_ogoal, ndel_ogoal, rep_ugoal, nrep_ugoal, rebalnce = struct.unpack(">LLLLLLLLLLLLL", data[:52])

            chunk_info = {
                'loop_start':                     loopstart,
                'loop_end':                       loopend,
                'invalid_deletions':              del_invalid,
                'invalid_deletions_out_of':       del_invalid+ndel_invalid,
                'unused_deletions':               del_unused,
                'unused_deletions_out_of':        del_unused+ndel_unused,
                'disk_clean_deletions':           del_dclean,
                'disk_clean_deletions_out_of':    del_dclean+ndel_dclean,
                'over_goal_deletions':            del_ogoal,
                'over_goal_deletions_out_of':     del_ogoal+ndel_ogoal,
                'replications_under_goal':        rep_ugoal,
                'replications_under_goal_out_of': rep_ugoal+nrep_ugoal,
                'replocations_rebalance':         rebalnce,
            }
            s.close()
        except Exception:
            traceback.print_exc(file=sys.stdout)


        # Filesystem check info
        check_info = {}
        try:
            s = self.bind_to_master()
            self.mysend(s, struct.pack(">LL", 512, 0))
            header = self.myrecv(s, 8)
            cmd, length = struct.unpack(">LL", header)
            if cmd == 513 and length >= 36:
                data = self.myrecv(s, length)
                loopstart, loopend, files, ugfiles, mfiles, chunks, ugchunks, mchunks, \
                msgbuffleng = struct.unpack(">LLLLLLLLL", data[:36])

                messages = ''
                truncated = ''
                if loopstart > 0:
                    if msgbuffleng > 0:
                        if msgbuffleng == 100000:
                            truncated = 'first 100k'
                        else:
                            truncated = 'no'
                        messages = data[36:]
                else:
                    messages = 'no data'
                check_info = {
                    'check_loop_start_time': loopstart,
                    'check_loop_end_time':   loopend,
                    'files':                 files,
                    'under_goal_files':      ugfiles,
                    'missing_files':         mfiles,
                    'chunks':                chunks,
                    'under_goal_chunks':     ugchunks,
                    'missing_chunks':        mchunks,
                    'msgbuffleng':           msgbuffleng,
                    'important_messages':    messages,
                    'truncated':             truncated,
                }
            s.close()
        except Exception:
            traceback.print_exc(file=sys.stdout)

        ret = {
            'info': info,
            'matrix': matrix,
            'chunk_info': chunk_info,
            'check_info': check_info,
        }
        return ret

    def mfs_servers(self):
        # Return list of chunk servers
        servers = []
        try:
            s = self.bind_to_master()
            self.mysend(s, struct.pack(">LL", CLTOMA_CSERV_LIST, 0))
            header = self.myrecv(s, 8)
            cmd, length = struct.unpack(">LL", header)
            if cmd == MATOCL_CSERV_LIST and self.masterversion >= (1, 5, 13) and (length % 54) == 0:
                data = self.myrecv(s, length)
                n = length/54

                for i in xrange(n):
                    d = data[i*54:(i+1)*54]
                    disconnected,v1,v2,v3,ip1,ip2,ip3,ip4,port,used,total,chunks,tdused,tdtotal,tdchunks, \
                    errcnt = struct.unpack(">BBBBBBBBHQQLQQLL",d)
                    strip = "%u.%u.%u.%u" % (ip1,ip2,ip3,ip4)

                    try:
                        host = (socket.gethostbyaddr(strip))[0]
                    except Exception as e:
                        host = "(unresolved)"
                        msg = 'Error during server hostname getting %s' % str(e)
                        logger.error(msg)
                        raise mfs_exceptions.MooseError(msg)

                    servers.append({
                            'host':           host,
                            'ip':             strip,
                            'port':           port
                        })

                return servers

            else:
                msg = 'Error during servers list obtainig. Check master version, it could be obsolite'
                logger.error(msg)
                raise mfs_exceptions.MooseError(msg)

        except Exception as e:
                msg = 'Error during connect to master: %s' % str(e)
                logger.error(msg)
                raise mfs_exceptions.MooseConnectionFailed(msg)
        finally:
            s.close()


    def mfs_backup_servers(self):
        # Return list of metaloggers servers
        metaloggers = []

        try:
            s = self.bind_to_master()
            self.mysend(s, struct.pack(">LL", 522, 0))
            header = self.myrecv(s, 8)
            cmd, length = struct.unpack(">LL", header)
            if cmd == MATOCL_MLOG_LIST and (length % 8) == 0:
                data = self.myrecv(s, length)
                n = length/8
                for i in xrange(n):
                    d = data[i*8:(i+1)*8]
                    v1, v2, v3, ip1, ip2, ip3, ip4 = struct.unpack(">HBBBBBB", d)
                    ip = '.'.join([str(ip1), str(ip2), str(ip3), str(ip4)])
                    ver = '.'.join([str(v1), str(v2), str(v3)])
                    try:
                        host = (socket.gethostbyaddr("%u.%u.%u.%u" % (ip1, ip2, ip3, ip4)))[0]
                    except Exception as e:
                        host = "(unresolved)"
                        msg = 'Error during server hostname getting %s' % str(e)
                        logger.error(msg)
                        raise mfs_exceptions.MooseError(msg)

                    metaloggers.append({ 'host': host,
                                         'ip':   ip
                                })
                    return metaloggers
            else:
                msg = 'Error during metaloggers list obtainig. Check master version, it could be obsolite'
                logger.error(msg)
                raise mfs_exceptions.MooseError(msg)

        except Exception as e:
            msg = 'Error during connect to master: %s' % str(e)
            logger.error(msg)
            raise mfs_exceptions.MooseConnectionFailed(msg)

        finally:
            s.close()


    def mfs_mounts(self):
        clients = []

        try:
            s = self.bind_to_master()
            self.mysend(s, struct.pack(">LLB", CLTOMA_SESSION_LIST, 1, 1))
            header = self.myrecv(s, 8)
            cmd, length = struct.unpack(">LL", header)
            if cmd == MATOCL_SESSION_LIST and self.masterversion >= (1, 5, 14):
                data = self.myrecv(s, length)
                statscnt = struct.unpack(">H", data[0:2])[0]
                pos = 2
                while pos < length:
                    sessionid, ip1, ip2, ip3, ip4, v1, v2, v3, ileng = struct.unpack(">LBBBBHBBL", data[pos:pos+16])
                    ipnum = "%d.%d.%d.%d" % (ip1, ip2, ip3, ip4)
                    ver = "%d.%d.%d" % (v1, v2, v3)
                    pos += 16
                    info = data[pos:pos+ileng]
                    pos += ileng
                    pleng = struct.unpack(">L", data[pos:pos+4])[0]
                    pos += 4
                    path = data[pos:pos+pleng]
                    pos += pleng

                    try:
                        host = (socket.gethostbyaddr(ipnum))[0]
                    except Exception:
                        host = "(unresolved)"
                    clients.append( {
                        'host':          host,
                        'ip':            ipnum,
                        'mount_point':   info,
                        'mfsmount_root': path
                    } )

                    return clients
            else:
                msg = 'Error during clients list obtainig. Check master version, it could be obsolite'
                logger.error(msg)
                raise mfs_exceptions.MooseError(msg)

        except Exception as e:
            msg = 'Error during connect to master: %s' % str(e)
            logger.error(msg)
            raise mfs_exceptions.MooseConnectionFailed(msg)

        finally:
            s.close()


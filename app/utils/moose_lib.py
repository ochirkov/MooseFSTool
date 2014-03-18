import socket
import struct
import time
import traceback
import sys

class MooseFS():
    """
    MooseFS class based on mfscgi script for encapsulate moose data manipulating.

    """

    def __init__(self, masterhost='mfsmaster', masterport=9421):
        self.masterhost = masterhost
        self.masterport = masterport
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
        msg = ''
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


    def mfs_info(self):

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

                result =  info_helper(total_space=total, avail_space=avail,
                                      trash_space=trspace, reserved_files=refiles,
                                      trash_files=trfiles, reserved_space=respace,
                                      all_fs_objects=nodes, chunks=chunks,
                                      regular_chunk_copies=tdcopies)

            elif length == 60:
                total, avail, trspace, trfiles, respace, refiles, nodes, dirs, files, chunks, \
                tdcopies = struct.unpack(">QQQLQLLLLLL", data)

                result = info_helper(total_space=total, avail_space=avail, files=files,
                                     trash_space=trspace, trash_files=trfiles, reserved_space=respace,
                                     reserved_files=refiles, regular_chunk_copies=tdcopies,  directories=dirs,
                                     all_fs_objects=nodes, chunks=chunks)

            elif length == 68:
                v1, v2, v3, total, avail, trspace, trfiles, respace, refiles, nodes, dirs, files, chunks, \
                allcopies, tdcopies = struct.unpack(">HBBQQQLQLLLLLLL", data)

                result =  info_helper(total_space=total, avail_space=avail, files=files,
                                      version='.'.join([str(v1), str(v2), str(v3)]), trash_space=trspace,
                                      trash_files=trfiles, reserved_space=respace, reserved_files=refiles,
                                      all_fs_objects=nodes, chunks=chunks, regular_chunk_copies=tdcopies,
                                      directories=dirs, all_chunk_copies=allcopies)

            elif length == 76:
                v1, v2, v3, memusage, total, avail, trspace, trfiles, respace, refiles, nodes, dirs, files, \
                chunks, allcopies, tdcopies = struct.unpack(">HBBQQQQLQLLLLLLL", data)

                result =  info_helper(memusage=memusage, total_space=total, avail_space=avail,
                                      version='.'.join([str(v1), str(v2), str(v3)]), trash_space=trspace,
                                      trash_files=trfiles, reserved_space=respace, reserved_files=refiles,
                                      all_fs_objects=nodes, chunks=chunks, regular_chunk_copies=tdcopies,
                                      directories=dirs, all_chunk_copies=allcopies, files=files)

                s.close()
            return result

        except Exception:
            traceback.print_exc(file=sys.stdout)
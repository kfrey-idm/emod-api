import json
import os

mydata = json.loads( open( "/home/jbloedow/Downloads/WORK/TBHIV/notebooks/TB_India_DTK/download/schema.json" ).read() )
def send( write_to_this ):
    #print( "Writing data to some fd." )
    if type(write_to_this) is int:
        """
        regular pipe
        data_as_str = json.dumps( mydata )
        ww = os.fdopen( write_to_this, 'w' )
        ww.write( data_as_str )
        ww.close()
        """
        # named pipe, already opened, file handle
        data_as_bytes = json.dumps( mydata ).encode('utf-8')
        num = os.write(write_to_this, data_as_bytes) # Write to Pipe
        print( f"Wrote {num} bytes to pipe." )
    elif type(write_to_this) is str:
        # we've been passed a filepath ot use to open a named pipe
        data_as_str = json.dumps( mydata )
        fifo_writer = open( write_to_this, "w" )
        fifo_writer.write( data_as_str )
        fifo_writer.close()
        import sys
        sys.exit()
    else:
        # regular pipe
        json.dump( mydata, write_to_this )
    #print( "DONE Writing data to some fd." )

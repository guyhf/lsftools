A python library with a set up tools to help in submitting and monitoring jobs
using LSF.

Also included are some scripts to summarize the queue:

  * hog : report on number of jobs per user
  * hogrun : report on number of currently running jobs
  * wherejobs : report on whos jobs are running on which nodes

To use lsftools:

    import lsftools
  
    commands = ["python myscript -n %d" % i for i in range(1,1000)]
    output_files = ["~/outdir/out_%d.txt" % i for i in range(1,1000)]

    lsftools.add_jobs(commands, output_files)
    lsftools.keep_jobs_running(commands, output_files, 100)

Other functions:

    run_commands(commands, filenames)
    run_commands_async(commands, filenames)

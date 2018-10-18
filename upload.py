# Just a stupid script to quickly upload a new version of the file
# to on my website.
# 
# The script should be ran from the folder containing the files.
# 
# Parameters:
# "-P": purge .bak, .cut, .log, .out, .toc and .aux files (be warned!).
# "-1": only compile 1 pass. (This assumes that you already have
#       an up-to-date .aux file in the temporary folder used by
#       this script; otherwise, 1 pass is not sufficient for
#       getting the references right.)
# "-d": disable TODOs.
# "-1l": only compile 1 pass, then don't upload.
# "-l": don't upload.
# "-n": do nothing, just purge.

import os
import sys
import shutil
import subprocess

dirlist = os.listdir("./")

versions = ["mlqs"]

if "-P" in sys.argv:
    print "Warning: purging working directory!"
    for fl in dirlist:
        flex = fl[-4:]
        if flex == ".aux" or flex == ".bak" or flex == ".cut" or flex == ".log" or flex == ".out" or flex == ".toc":
            print "removing ", fl
            os.remove(fl)
    dirlist = os.listdir("./")

if "-n" in sys.argv:
    sys.exit("Exiting successfully since -n attribute was specified.")

starting_folder = os.getcwd()

for vernum in versions:
    print ""
    print "Compiling " + vernum + "..."
    print ""
    os.chdir(starting_folder)
    fl = vernum + ".tex"
    fll = vernum + "-long.tex" # This file will be created in the temp folder;
                               # no such file should exist in the source folder.

    passes = 4
    if "-1" in sys.argv or "-1l" in sys.argv:
        passes = 1
    
    local = False
    if "-l" in sys.argv or "-1l" in sys.argv:
        local = True
    
    with open(fl) as search:
        forbidden = "\includecomment{verlong}"
        for line in search:
            line = line.rstrip()  # remove '\n' at end of line
            if line == forbidden:
                sys.exit("verlong is active!")
    
    # create temporary folder for compiling
    tempdirname = os.path.expanduser("~/.python_temp_" + vernum)
    if passes >= 4:
        # clean the temporary folder, since we are going to do
        # enough passes:
        try:
            shutil.rmtree(tempdirname)
        except OSError:
            pass
        os.mkdir(tempdirname)
    shutil.copyfile(fl, tempdirname + "/" + fl)
    shutil.copyfile("queue.bib", tempdirname + "/queue.bib")
    shutil.copyfile("sec-JT-old.tex", tempdirname + "/sec-JT-old.tex")
    
    # only work with temporary file from now on
    os.chdir(tempdirname)
    
    if "-d" in sys.argv: # bowdlerize the file for publication:
        fltemp2 = vernum + "-temp.tex"
        with open(fl) as old:
            try:
                os.remove(fltemp2)
            except OSError:
                pass
            with open(fltemp2, "a") as new:
                for line in old:
                    new.write(line.replace(r"\usepackage[colorinlistoftodos]{todonotes}", r"\usepackage[colorinlistoftodos,disable]{todonotes}"))
                    r"""
                    if r"\maketitle" in line:
                        new.write("\n")
                        new.write(r"{\Large \textbf{UNFINISHED DRAFT!} \\ We are still working on this paper; parts of it may still get rewritten. -- Darij, \today}" + "\n\n")
                    """
        shutil.copyfile(fltemp2, fl)
    
    fl_pdf = fl[:-4] + ".pdf"

    # compile the short version
    for i in range(passes):
        p = subprocess.Popen(["pdflatex", fl])
        try:
            p.wait()
        except KeyboardInterrupt:
            try:
               p.terminate()
            except OSError:
               pass
            print "Compilation aborted!"
            sys.exit()
        if i == 0: # compile bib
            p = subprocess.Popen(["bibtex", vernum + ".aux"])
            p.wait()
    # copy the PDF file into home folder
    os.system("cp " + fl_pdf + " " + starting_folder + "/" + fl_pdf)

    # create the long version
    with open(fl) as old:
        try:
            os.remove(fll)
        except OSError:
            pass
        with open(fll, "a") as new:
            for line in old:
                new.write(line.replace(r"\excludecomment{verlong}", r"\includecomment{verlong}").replace(r"\includecomment{vershort}", r"\excludecomment{vershort}").replace(r"\title[MLQs with spectral parameters]{Multiline queues with spectral parameters}", r"\title[MLQs with spectral parameters]{Multiline queues with spectral parameters [detailed version]}"))

    fll_pdf = fll[:-4] + ".pdf"

    # compile the long version
    for i in range(passes):
        p = subprocess.Popen(["pdflatex", fll])
        try:
            p.wait()
        except KeyboardInterrupt:
            try:
               p.terminate()
            except OSError:
               pass
            print "Compilation aborted!"
            sys.exit()
        if i == 0: # compile bib
            p = subprocess.Popen(["bibtex", vernum + "-long.aux"])
            p.wait()
    # copy the PDF file into home folder
    os.system("cp " + fll_pdf + " " + starting_folder + "/" + fll_pdf)

    if not local:
        # copy the files into website folder
        os.system("cp " + fl_pdf  + " /cygdrive/d/math/mats/website/algebra/" + fl_pdf)
        os.system("cp " + fll_pdf  + " /cygdrive/d/math/mats/website/algebra/" + fll_pdf)
        import zipfile # zipping the source:
        zipf = zipfile.ZipFile("mlqs.zip", 'w', zipfile.ZIP_DEFLATED)
        zipf.write(fl)
        zipf.write("queue.bib")
        zipf.write("sec-JT-old.tex")
        zipf.close()
        os.system("cp mlqs.zip /cygdrive/d/math/mats/website/algebra/mlqs.zip")
        print "Upload to CIP servers:"
        os.system("scp mlqs.zip " + fl_pdf + " " + fll_pdf + " grinberg@remote.cip.ifi.lmu.de:~/public_html/algebra")
    r"""
        print "Upload to UMN servers:"
        os.system("scp " + fl + " " + fl_pdf + " dgrinber@remote.math.umn.edu:~/www/")
    """


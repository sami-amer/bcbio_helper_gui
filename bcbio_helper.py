"""
bcbio_helper

Usage:
    bcbio_helper.py (-i)
    bcbio_helper.py (<data_path>) (<fasta_path>) (<gtf_path>) [options] (<run_name>) (<outpath>)


Options:
    -i                        activates interactive mode
    --analysis=<str>          sets the analysis mode for bcbio (default: RNA-seq)
    --genome=<str>            sets the genome for bcbio (default: hg38)
    --adapter=<str/list>      sets the adapters for bcbio (default: [nextera, polya])
    --strandedness=<str>      sets the strandedness for bcbio (default: unstranded)
    --aligner=<str>           sets the aligner for bcbio (default: hisat2)
    --cores=<int>             allocates the number of cores that bcbio may use (default: 12)

"""

# native
import csv
import os
from pathlib import Path
import subprocess
import yaml

# pkg
from docopt import docopt

#lib
# from deseq_helper import deseq_helper


def create_csv(outpath, path_to_data, run_name):
    """
    Creates a csv mapping samplename (path) to a description (can be anything, we choose name of sample)

        Arguments:
            
            outpath      (Path): path to the output directory
            path_to_data (Path): path to the folder that contains the fastQ files
            run_name     (str): name of the run

        Returns:

            csv (None): creates a csv file with samplename, description
            csv_path (Path): path to the newly created csv
            
    """
    # by default, will look for gz files
    # ! Reminder: this will only look for forward reads, this is by design.
    # ! BCBIO will find reverse reads on its own, as long as they are there.
    items = [x for x in path_to_data.glob("**/*1.fq.gz") if x.is_file()]  
    
    if not items:
        raise ValueError("Can't find zipped FASTQ data! (*.fq.gz)")

    with open(outpath / run_name, "w+") as csvfile: # opens a file to write to
    
        writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL) # creates the writer with the correct delimiters
        writer.writerow(["samplename", "description"]) # creates the header row
    
        for item in items: # iterates through items and writes them
            samplename = item
            description = item.name.split("_")[0]
            writer.writerow([samplename, description])
    
        print(f"CSV stored to {os.getcwd() + str(outpath)}\n\n") # tells us we succeeded and where to find the csv
    
    return outpath / run_name # returns the path to the csv


def get_args(args):
    """
    Gets the arguments from the command line and makes them YAML ready.
    Is not called when running with the `-i` flag.

        Arguments:

            args (dict): dict as created by docopt

        Returns:

            args (dict): a yaml.dump() ready dict with nested dicts and lists
    """

    # override default value only if an override was given
    analysis = args["--analysis"] if args["--analysis"] else "RNA-seq"
    genome_build = args["--genome"] if args["--genome"] else "hg38"
    aligner = args["--aligner"] if args["--aligner"] else "hisat2"
    adapter = args["--adapter"] if args["--adapter"] else ["nextera", "polya"]
    strandedness = args["--strandedness"] if args["--strandedness"] else "unstranded"

    args = { # this is nested very specfically to work with bcbio
        "details": [
            {
                "analysis": analysis,
                "genome_build": genome_build,
                "algorithm": {
                    "transcriptome_fasta": args["<fasta_path>"],
                    "transcriptome_gtf": args["<gtf_path>"],
                    "aligner": aligner,
                    "adapters": adapter,
                    "strandedness": strandedness,
                },
            }
        ],
        "upload": {"dir": args["<outpath>"] + "final/"}
    }
    return args # returns a dictionary that is ready to be dumped


def create_template(outpath, args):
    """
    Creates the template YAML BCBIO needs to create the run YAML.


        Arguments:

            outpath (Path): path to the output directory
            args    (dict): a yaml.dump() ready dict with nested dicts and lists
        
        Returns:

            yaml      (None): creates a template for bcbio to use
            yaml_path (Path): path to newly created yaml
    """

    with open(outpath / "template.yaml", "w+") as file: # opens a file to write to
        
        yaml.dump(args, file, sort_keys=False) # this takes care of all the writing 
        
        print("Here are the contents of the produced YAML file: \n\n") 
        print(yaml.dump(args) + "\n\n") # we print out the YAML for debugging purposes

    return outpath / "template.yaml" # returns the path to the YAML


def create_run_yaml(path_to_data, path_to_yaml, path_to_csv, outpath):
    """
    Invokes bcbio to create the YAML needed to run alignment and analysis

        Arguments:

            path_to_data (Path): path to the folder that contains the fastQ files
            path_to_yaml (Path): path to the template YAML created with `create_template()`
            path_to_csv  (Path): path to the csv created with `create_csv()`
            outpath      (Path): path to the output directory

        Returns:

            yaml (None): creates a YAML to run bcbio with
    """
    
    os.chdir(outpath) # changes working directory to keep everything contained
    
    create_run_yaml = subprocess.run( # uses the subprocess module to run bcbio YAML creation
        [
            "bcbio_nextgen.py",
            "-w",
            "template",
            str(".." / path_to_yaml), # subproccess does not take Path objects
            str(".." / path_to_csv),
            str(".." / path_to_data),
        ]
    )
    
    print("Created run YAML")
    
    os.chdir("..") # changes the directory back to avoid any issues


def start_bcbio(outpath, run_name, cores):
    """
    Runs the bcbio command to being alignment and analysis

        Arguments:
            outpath  (Path): path to the output directory
            run_name (str): name of the run
            cores    (str): number of cores allocated for bcbio
        
        Returns:
            
            None (None): this only runs bcbio, which has its associated returns
    """
    
    
    os.chdir(outpath / str(run_name).split(".")[0] / "work") # changes to the work directory
    start_bcbio = subprocess.run( # uses subproccess to run bcbio
        [
            "bcbio_nextgen.py",
            f"../config/{str(run_name).split('.')[0]}.yaml",
            "-n",
            cores,
        ]
    )
    os.chdir("../../../") # changes back to original directory


def main(arguments):
    """
    Takes the command line arguments through docopt, and runs each submodule

        Arguments:

            arguments (dict): dict as parsed by docopt

        Returns:
            
            None (None): this runs bcbio, which has its associated returns

    """
    args = get_args(arguments)
    cores = arguments["--cores"] if arguments["--cores"] else str(12)
    
    run_name = (
        Path(arguments["<run_name>"])
        if arguments["<run_name>"].split(".")[-1] == "csv"
        else Path(arguments["<run_name>"] + ".csv")
    )

    outpath = Path(arguments["<outpath>"])
    if not os.path.isdir(outpath):
        os.mkdir(outpath)
    
    data_path = Path(arguments["<data_path>"])
    csv_path = create_csv(outpath, data_path, run_name)
    template_path = create_template(outpath, args)
    create_run_yaml(data_path, template_path, csv_path, outpath)
    
    start_bcbio(outpath, run_name, cores)


def main_interactive():
    """
    Takes the inputs through python inputs, uses default values for YAML

        Arguments:

            None (None): exclusivley uses python inputs

        Returns:
            
            None (None): this runs bcbio, which has its associated returns

    """

    print("\nYou have activated interactive mode: bcbio_helper.\n"
    "Interactive mode can only use default bcbio arguments (hg38, hisat2, polya, unstranded)\n"
    "If you would like to use command-line arguments, please execute `bcbio_helper.py --help` and follow that template\n"
    "Press Control+C at any time to cancel this input sequence\n")
    
    cont = input("Would you like to continue [y/n]? ").lower()

    while cont == "y":
    
        data_path = Path(input("Enter path to FASTQ data: "))
        fasta_path = str(Path(input("Enter path to the transciptome FASTA: ")))
        gtf_path = str(Path(input("Enter path to the transciptome gtf: ")))
        outpath = Path(input("Enter your output directory: "))
        
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        
        run_name = input("Enter the name of your run: ")
        run_name = Path(run_name) if run_name.split(".")[-1] == "csv" else Path(run_name + '.csv')
        cores = input("Enter the number of vCPUS/Cores you want to use: ")

        args = {
            "details": [
                {
                    "analysis": 'RNA-seq',
                    "genome_build": 'hg38',
                    "algorithm": {
                        "transcriptome_fasta": fasta_path,
                        "transcriptome_gtf": gtf_path,
                        "aligner": 'hisat2',
                        "adapters": ['polya'],
                        "strandedness": 'unstranded',
                    },
                }
            ],
            "upload": {"dir": str(outpath) + "final/"}
        }

        print(
            "\n\nThese are your parameters: \n\n"
            f"Path to data: {data_path}\n"
            f"Path to FASTA: {fasta_path}\n"
            f"Path to GTF: {gtf_path}\n"
            f"Output Directory: {outpath}\n"
            f"Name of Run: {run_name}\n"
            f"Number of Cores: {cores}\n")
        
        cont = input("Would you like to continue [y/n]? ").lower()
        if cont != "y": break

        csv_path = create_csv(outpath, data_path, run_name)
        template_path = create_template(outpath, args)
        create_run_yaml(data_path, template_path, csv_path, outpath)
        start_bcbio(outpath, run_name, cores)

    print("Exiting...")


if __name__ == "__main__":
    
    # parse arguments
    arguments = docopt(__doc__)
    
    # check which mode and run
    if arguments["-i"]:
        main_interactive()
    
    else:
        main(arguments)
    
    # ? Metadata detection, ask Ajit

    # python bcbio_helper.py -i
    
    # python bcbio_helper.py data/ genomes/Homo_sapiens.GRCh38.cdna.all.fa genomes/Homo_sapiens.GRCh38.96.chr.gtf run_1 seq/
    
    # python bcbio_helper.py data/ genomes/Homo_sapiens.GRCh38.cdna.all.fa genomes/Homo_sapiens.GRCh38.96.chr.gtf 
    #       --analysis=RNA-seq --genome=hg38 --adapter=nextera --aligner=hisat2 --strandedness=unstranded
    #       run_1 seq/

    # ? Notes for v2
    # ?     Merge both doctor and helper to two differnt commands one one script
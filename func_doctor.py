"""
bcbio_doctor

Usage:
    bcbio_doctor.py [<genomes_path>]
    bcbio_doctor.py (-d)  [--gtf] [--gtf_chr] [--cdna] <output_path>

Options:
    -d              runs the download script
    --gtf           in download mode, downloads the gtf file with no CHR annotation
    --gtf_chr       in download mode, downloads the gtf file with CHR annotation
    --cdna          in download mode, downloads the cdna.fa file
    <genomes_path>  if you would like bcbio_doctor to check genomes, provide a path. otherwise this step is skipped
    <output_path>   path where you want the genes to go
"""

# native
import csv
import fnmatch
import glob
import os
from pathlib import Path, PurePath
import requests
import subprocess

# pkg
from docopt import docopt
import yaml  # included with anaconda
from tqdm import tqdm  # included with anaconda



def check_PATH():
    """
    Checks the PATH variable of the current environment, and lets you know if something is wrong

        Arguments:

            None

        Returns:
            
            bcbio_path (Path):  returns the path to the bcbio installation
    """
    
    env_paths = set(os.environ["PATH"].split(":")) # makes the paths into a set to remove duplicates

    req_paths = {
        "bcbio/tools/bin": [False, True],
        "bcbio/anaconda/bin": [False, False],
        "bcbio": [False, False],
    } # initializes the paths we want to look for

    matching = fnmatch.filter(env_paths, "*/bcbio/**") + fnmatch.filter(
        env_paths, "*/bcbio"
    ) # checks if there are any matches
    matching = [Path(x) for x in matching] # casts them to Paths

    bcbio_bin_path = None
    
    for path in matching:
        
        if fnmatch.fnmatch(path, "**/bcbio/tools/bin"):
            bcbio_path = Path(*path.parts[:-2]) # gets the path to bcbio installation
            req_paths["bcbio/tools/bin"][0] = True
        
        elif fnmatch.fnmatch(path, "**/bcbio/anaconda/bin"):
            req_paths["bcbio/anaconda/bin"][0] = True
        
        elif fnmatch.fnmatch(path, "**/bcbio"):
            req_paths["bcbio"][0] = True

    print(
        "Here are the results of the $PATH Search. Paths marked critical are required for bcbio to operate correctly.\n"
    )

    for path in req_paths:
        print(path + "\t\t", end="", flush=True)

        print("CRITICAL\t", end="", flush=True) if req_paths[path][1] else print(
            "\t", end="", flush=True
        )

        print("\t\t", end="") if path == "bcbio" else None

        print(" FOUND") if req_paths[path][0] else print(" NOT FOUND")

    print(
        "\nIf the above does not look correct, you may follow the steps for problem 1 in `bcbio_debugging.md`, but do so at your own discretion."
    )
    return bcbio_path # returns our bcbio_path


def check_genome_paths(bcbio_path):
    """
    Checks to make sure the genomes are present in the bcbio installation

        Arguments:
            
            bcbio_path (Path):  the path to the bcbio_installation

        Returns:

            None
    """
    run_directory = os.getcwd() # remembers the current working directory
    os.chdir(bcbio_path) # navigates to bcbio installation
    print("genomes FOUND in bcbio: ") if (glob.glob("genomes/*/*")) else print(
        "genomes NOT FOUND!"
    )
    for genome in glob.glob("genomes/*/*"):
        print(Path(genome).name)

    if ("galaxy/tool-data/sam_fa_indices.loc") not in (
        glob.glob("galaxy/**/**")
    ):
        print(
            "`sam_fa_indices.loc NOT FOUND! Check problem 2 in `bcbio_debugging.md`"
        )  # Do I need this to catch other things?

    os.chdir(run_directory) # returns to the original working directory


def download_genes(download_path, to_download):  # Make this work on command-line
    """
    Downloads any genes specified on the command line

        Arguments:

            download_path (Path):   where to download the files to
            to_download   (list):   a list of the files to download

        Returns:

            files (None):   downloads the files specified to download_path

    """
    download_info = { # initilaizes info of the files, as seen in the debugging manual
        "cdna": {
            "url": "http://ftp.ensembl.org/pub/release-96/fasta/homo_sapiens/cdna/Homo_sapiens.GRCh38.cdna.all.fa.gz",
            "name": "Homo_sapiens.GRCh38.cdna.all.fa.gz",
        },
        "gtf": {
            "url": "http://ftp.ensembl.org/pub/release-96/gtf/homo_sapiens/Homo_sapiens.GRCh38.96.gtf.gz",
            "name": "Homo_sapiens.GRCh38.96.gtf.gz",
        },
        "gtf_chr": {
            "url": "https://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/genes/hg38.ncbiRefSeq.gtf.gz",
            "name": "hg38.ncbiRefSeq.gtf.gz",
        },
    }

    for file in to_download: # downloads each file
        file_name = download_info[file]["name"]
        file_url = download_info[file]["url"]
        download_url(file_url, download_path / file_name, file_name)


def download_url(url, output_path, fname):
    """
    Helper function for download_genes

        Arguments:

            url         (str): the url to download from
            output_path (Path): the path to download to
            fname       (str): what name to save the downloaded file to

        Returns:

            file (None): only downloads the file
    """
    
    r = requests.get(url, stream=True) # initiates the stream
    total = int(r.headers.get("content-length", 0)) # gets the size of the file

    if not os.path.isdir(output_path.parent): # creates directory if needed
        os.mkdir(output_path.parent)

    with open(output_path, "wb") as file, tqdm( # downloads with download bar
        desc=fname,
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in r.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def check_gene_names(path_to_genomes):
    """
    Checks the gene names in all fasta files in the specified folder

        Arguments:

            path_to_genomes (Path):  where all the fasta files are stored

        Returns:

            None
    """
    paths = path_to_genomes.glob("*.fa") # gets all fasta files
    for path in paths:
        with open(path, "r") as f:
            for line in f:
                gene_name = line.split(" ")[0]
                break
            if "." in gene_name:
                print(
                    path.name + " is in the format: XXXXXXXX.XX\n"
                    "If this does not match your fastQ file, please take a look at remove_versions.py"
                )
            else:
                print(
                    path.name + " is in the format: XXXXXXXX"
                ) # currently no solution for adding version numbers, but this shouldn't (?) matter


def check_gene_annotation(path_to_genomes):
    """
    Checks the gene annotation of all gtf files in the specified folder

        Arguments:

            path_to_genomes (Path):  where all the fasta files are stored

        Returns:

            None
    """
    paths = path_to_genomes.glob("*.gtf") # gets all gtf files

    for path in paths:
        with open(path, "r") as f:
            for line in f:
                if line[0] == "#":
                    continue
                else:
                    gene_annotation = line.split("\t")[0]
                    break
        if "chr" in gene_annotation:
            print(path.name + " is annotated: chrX")
        else:
            print(path.name + " is annotated: X")

    print("\nYou can download a non-chr format with: bcbio_doctor.py -d --gtf_chr\n")

    print(
        "You can download a chr format with: bcbio_doctor.py -d --gtf_chr \n\n"
        "You can also run the following command to edit the annotation, although this is less reliable: \n\t"
        r"""awk 'OFS="\t" {if (NR > 5) $1="chr"$1; print}' input_name.gtf > output_name.gtf"""
    )


def main():
    # TODO: Make thsi function take an arguments dict that mirror the docopt args.
    # TODO: Make this callable from app_helper.py
    
    arguments = docopt(__doc__)

    if arguments["-d"]: # if we are running the download script
        download_path = Path(arguments["<output_path>"])
        to_download = []

        to_download.append("cdna") if arguments["--cdna"] else None
        to_download.append("gtf") if arguments["--gtf"] else None
        to_download.append("gtf_chr") if arguments["--gtf_chr"] else None

        if not to_download:  # check if we have any inputs and return error if nothing
            print("No files specified for download")
        else:
            print("Running download script...")
            download_genes(download_path, to_download)

    else:  # its either download or diagnose, never both

        print("_" * 25 + "\n")
        bcbio_path = check_PATH()
        print("_" * 25 + "\n")
        check_genome_paths(bcbio_path)
        print("_" * 25 + "\n")

        if arguments["<genomes_path>"]:
            genomes_path = Path(arguments["<genomes_path>"])
            check_gene_names(genomes_path)
            print("_" * 25 + "\n")
            check_gene_annotation(genomes_path)
            print("_" * 25 + "\n")


if __name__ == "__main__":
    main()

    # ? TODO for v2
    # ? Talk to peter about merging the two together
    # ? Make slide deck pretty
    # ? Add verbose logging

    # python bcbio_doctor.py
    
    # python bcbio_doctor.py genomes
    
    # python bcbio_doctor.py -d --gtf --cdna --gtf_chr test_genomes

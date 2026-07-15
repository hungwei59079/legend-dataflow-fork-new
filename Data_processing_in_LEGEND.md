# Data Processing in LEGEND

## LEGEND Data, Ref Cycles and Tiers

### Location
Check the `computing` tab on Confluence for more information: https://legend-exp.atlassian.net/wiki/spaces/LEGEND/pages/261750968/Computing

For NERSC, the data is located at `/global/cfs/cdirs/m2676/data/lngs/l200/public/`.

### File Hierarchy

#### Top level: `prodenv`
At the time I'm writing this document, the file hierarchy looks like this (three levels):
```
.
├── prodenv
│   ├── containers
│   │   (skipped)
│   ├── filelists
│   │   (skipped)
│   ├── jl-prod-orig
│   │   └── ref
│   ├── prod-blind
│   │   ├── auto
│   │   ├── ref
│   │   └── tmp
│   └── prod-orig
│       └── ref
└── sandbox -> ../private/sandbox
```

The `prod-blind` directory stores most of the data we need. The generated data are separated into three categories: `auto`, `ref`, and `tmp`, which correspond to different levels of stability. The stable, released data are in `ref`.

#### Production cycles inside `ref`
Let's look inside `ref` (only partially listed):
```
(legend-dataflow) hungwei@login38:~/l200/public/prodenv/prod-blind/ref> ls -l
lrwxrwxrwx  1 lgdata legend     6 Jan 25 08:22 latest -> v2.1.5
lrwxrwxrwx  1 lgdata legend     6 May 22 06:59 napoli26 -> v3.3.0
drwxr-s--x  6 lgdata legend  4096 Jan 25 08:17 v1.0.0
drwxr-s--x  6 lgdata legend  4096 Jun  8 13:08 v1.0.1
drwxr-s--x  6 lgdata legend 16384 Jan 25 21:33 v2.0.0
drwxr-s--x  7 lgdata legend  4096 Jan 25 21:34 v2.1.0
drwxr-s--x  6 lgdata legend  4096 Jan 25 08:18 v2.1.1
drwxr-s--x  6 lgdata legend  4096 Jan 25 08:18 v2.1.2
```
Each directory is one production cycle: a snapshot of the `legend-dataflow` workflow together with the inputs it used and the data it generated. The version tag does not align with the version of the `legend-dataflow` repository. I'm not sure which package's version these tags correspond to, but we can at least easily tell which dataset is older and which is newer.

#### Inside a production cycle
If you `cd` into any one of these, you will probably see the following (only the important entries are listed):
```
(legend-dataflow) hungwei@login38:~/l200/public/prodenv/prod-blind/ref/v3.0.0> ls -l
total 86
-rw-r----- 1 lgdata legend  2687 Feb  6 16:36 dataflow-config.yaml
drwxr-s--- 3 lgdata legend  4096 Sep 16  2025 docs
drwxr-s--- 7 lgdata legend  4096 Sep  1  2025 generated
drwxr-s--- 9 lgdata legend 16384 Aug 31  2025 inputs
drwxr-s--- 5 lgdata legend  4096 Sep 16  2025 workflow
```

##### Explanation
- `workflow` and `dataflow-config.yaml`: Snakemake stuff. Explained in the next section.
- `docs`: Documents you can read if you're interested in how `legend-dataflow` works.
- `generated`: Generated data. **LOOK FOR DATA HERE**
- `inputs`: Metadata and configs. This is where you can find the expression used to compute each output field of the LH5 files.

#### Inside `generated`
Finally, look inside `generated`:
```
(legend-dataflow) hungwei@login38:~/l200/public/prodenv/prod-blind/auto/v2.0.0/generated> tree -L 3 -d -I 'log|benchmark'
.
├── par
│   ├── dsp
│   │   ├── cal
│   │   ├── lac
│   │   ├── phy
│   │   ├── rdc
│   │   ├── ssc
│   │   └── tst
│   ├── filedb
│   ├── hit
│   │   └── cal
│   ├── pht
│   └── psp
├── plt
│   ├── dsp
│   │   └── cal
│   └── hit
│       └── cal
├── tier
│   ├── dsp
│   │   ├── bkg
│   │   ├── cal
│   │   ├── fft
│   │   ├── hvs
│   │   ├── lac
│   │   ├── lac_old
│   │   ├── phy
│   │   ├── pul
│   │   ├── pzc
│   │   ├── rdc
│   │   ├── ssc
│   │   └── tst
│   ├── evt
│   │   ├── bkg
│   │   ├── cal
│   │   ├── fft
│   │   ├── hvs
│   │   ├── lac
│   │   ├── lac_old
│   │   ├── old_lac
│   │   ├── phy
│   │   ├── pul
│   │   ├── pzc
│   │   ├── rdc
│   │   ├── ssc
│   │   └── tst
│   ├── hit
│   │   ├── bkg
│   │   ├── cal
│   │   ├── fft
│   │   ├── hvs
│   │   ├── lac
│   │   ├── lac_old
│   │   ├── phy
│   │   ├── pul
│   │   ├── pzc
│   │   ├── rdc
│   │   ├── ssc
│   │   └── tst
│   ├── raw -> ../../../../ref/v3.0.0/generated/tier/raw
│   └── tcm
│       ├── bkg
│       ├── cal
│       ├── fft
│       ├── hvs
│       ├── lac
│       ├── phy
│       ├── pul
│       ├── pzc
│       ├── rdc
│       ├── ssc
│       └── tst
```

##### Explanation
- First level — `par`, `tier`, `plt`, `log`, `tmp`: `par` means parameters, which store the calibration results such as the ADC/keV ratio in the hit tier. `tier` is where you find the generated LH5 files, `log` and `tmp` are literally what they say they are, and `plt` holds the diagnostic plots produced during calibration, which is why it only contains `cal` subdirectories.
- Second level — `hit`, `dsp`, `evt`, etc.: See the next section.
- Third level — `cal`, `phy`, `pul`, `ssc`, etc.: Datatype. Usually represents different experimental conditions. `cal` and `phy` are the standard ones. For `cal` data we put sources into all source insertion systems, and we use this portion of the data for calibration. For `phy` data we don't put in any sources, and these are the ones that should be used for the final physics analysis. The others are special runs. For example, `ssc` only exists in r16: each run only lasts 12 hours, and we only put a single source into the system. Information about each run can be found on the QCP: Data Taking page: https://legend-exp.atlassian.net/wiki/spaces/LEGEND/pages/1599963139/QCP+Data+Taking

## The legend-dataflow repository

URL: https://github.com/legend-exp/legend-dataflow

We will only talk about it briefly here. Read its README for more information.

All the LEGEND data stored in the manner described above are generated by `legend-dataflow` using Snakemake. You can think of this repository as the main script, and of all the other packages such as `dspeed`, `pygama`, and `lgdo` as merely its dependencies. They only provide functions that are imported into the scripts within this repository.

### The `workflow/` directory
We have already explained the other directories in this repository (`inputs`, `generated`, etc.). Let's now look at `workflow/`:

```
workflow/
├── profiles
│   ├── default
│   ├── lngs
│   ├── lngs-build-raw
│   └── sator
├── __pycache__
├── rules
│   ├── ann.smk
│   ├── blinding_calibration.smk
│   ├── blinding_check.smk
│   ├── channel_merge.smk
│   ├── common.smk
│   ├── dsp_pars_geds.smk
│   ├── dsp_pars_spms.smk
│   ├── dsp.smk
│   ├── evt.smk
│   ├── hit_pars_geds.smk
│   ├── hit.smk
│   ├── main.smk
│   ├── (......)
└── src
```
This directory contains the `Snakefile` and the rule files (`*.smk`). After running the `snakemake` command with a specified target, Snakemake searches through all the rules it has and attempts to build a DAG (directed acyclic graph) that lists the steps needed to create the final output from the existing inputs. A rule block might look like this:
```
rule autogen_output:
    input:
        filelist=Path(filelist_path(config)) / "{label}-{tier}.filelist",
    output:
        gen_output="{label}-{tier}.gen",
        summary_log=Path(log_path(config))
        / f"summary-{{label}}-{{tier}}-{timestamp}.log",
        warning_log=Path(log_path(config))
        / f"warning-{{label}}-{{tier}}-{timestamp}.log",
    log:
        Path(tmp_log_path(config)) / time / "{label}-{tier}-complete_run.log",
    threads: min(workflow.cores, 64)
    params:
        valid_keys_path=Path(pars_path(config)) / "valid_keys",
        filedb_path=Path(pars_path(config)) / "filedb",
        ignore_keys_file=Path(det_status) / "ignored_daq_cycles.yaml",
        setup=lambda wildcards: config,
        basedir=workflow.basedir,
    script:
        "../src/legenddataflow/scripts/flow/complete_run.py"
```
A lot of "wildcards" need to be replaced with correctly computed values. Those are handled by Snakemake.

### Reconstructing the workflow with dry runs
However, for those of us who just want to know how the procedure is structured, going through the computation ourselves is not appealing. Therefore, I forked the dataflow repo and tried doing some dry runs myself. (Repo URL: https://github.com/hungwei59079/legend-dataflow-fork-new)

![Local Image](legend-dataflow.png)
Source: https://legend-exp.atlassian.net/wiki/spaces/LEGEND/pages/812187742/LEGEND-200+Data


From this flow chart, I gather that the final target should be `evt`. (Technically, `skm` is the highest tier. However, `skm` is built from the concatenated `pet` tier, which in turn requires `pht` and `psp` — the partition versions of `evt`, `hit`, and `dsp` respectively. I need to understand partitions better before I can work out that part of the workflow.) I used an AI-generated script to parse the output of the Snakemake dry run, and eventually got something like this: 
```
Step 1 [stage 0]: rule build_pars_dsp_tau_spms (155 jobs)
Input: /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/raw/phy/p03/r001/l200-p03-r001-phy-20230318T015140Z-tier_raw.lh5, /global/u2/h/hungwei/legend-dataflow-new/inputs/dataprod/overrides/dsp/cal/p03/r000/l200-p03-r000-cal-T%-par_dsp-overwrite.yaml
   ... (+ 773 more items)
Output: /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/par/dsp/phy/p03/r001/l200-p03-r001-phy-20230318T015140Z-par_dsp_spms.yaml, /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/par/dsp/phy/p03/r001/l200-p03-r001-phy-20230318T025144Z-par_dsp_spms.yaml
   ... (+ 153 more items)
Script/Shell: Shell command: PRODENV=/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0 LGDO_BOUNDSCHECK=false DSPEED_BOUNDSCHECK=false PYGAMA_PARALLEL=false PYGAMA_FASTMATH=false TQDM_DISABLE=true /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/.snakemake/legend-dataflow/venv/bin/par-spms-dsp-trg-thr-multi  
(...... a lot more flags)
----------------------------------------
Step 2 [stage 0]: rule build_svm_dsp_geds (1 jobs)
Input: None
Output: /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/par/dsp/cal/p03/r001/l200-p03-r001-cal-20230317T211819Z-par_dsp_svm.pkl
(30 more steps)
```
This tells us in detail exactly what is done between the raw data and the evt tier. Now we know which shell script to look at.

## Example: `build_evt` rule breakdown

### The dry-run entry for `build_evt`
My work is related to cross-talk correction, which is done in the event tier, so I looked into `build_evt`. It is the final step of the DAG:
```
Step 30 [stage 19]: rule build_evt (155 jobs)
Input: /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/dsp/phy/p03/r001/l200-p03-r001-phy-20230318T015140Z-tier_dsp.lh5, /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/hit/phy/p03/r001/l200-p03-r001-phy-20230318T015140Z-tier_hit.lh5
   ... (+ 1548 more items)

Output: /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/evt/phy/p03/r001/l200-p03-r001-phy-20230318T015140Z-tier_evt.lh5, /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/evt/phy/p03/r001/l200-p03-r001-phy-20230318T025144Z-tier_evt.lh5
   ... (+ 153 more items)

Script/Shell: Shell command: 
PRODENV=/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0 
LGDO_BOUNDSCHECK=false 
DSPEED_BOUNDSCHECK=false 
PYGAMA_PARALLEL=false 
PYGAMA_FASTMATH=false 
TQDM_DISABLE=true 

/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/.snakemake/legend-dataflow/venv/bin/build-tier-evt 
--configs /global/u2/h/hungwei/legend-dataflow-new/inputs/dataprod/config 
--metadata /global/u2/h/hungwei/legend-dataflow-new/inputs 
--log /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tmp/log/20260710T005348Z/tier_evt/l200-p03-r001-phy-20230321T165925Z-tier_evt.log 
--tier evt 
--datatype phy 
--timestamp 
20230321T165925Z 
--xtc-file /global/u2/h/hungwei/legend-dataflow-new/inputs/dataprod/overrides/evt/xtc/p08/r015/l200-p08-r015-xtc-T%-par_evt_xtc.lh5 
--par-files /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/par/hit/cal/p03/r001/l200-p03-r001-cal-20230317T211819Z-par_hit.yaml /global/u2/h/hungwei/legend-dataflow-new/inputs/dataprod/overrides/hit/lar/p03/r000/l200-p03-r000-lar-T%-par_hit-overwrite.yaml /global/u2/h/hungwei/legend-dataflow-new/inputs/dataprod/overrides/hit/cal/p03/r000/l200-p03-r000-cal-T%-par_hit-overwrite.yaml /global/u2/h/hungwei/legend-dataflow-new/inputs/dataprod/overrides/hit/blind/p03/r000/l200-p03-r000-cal-T%-par_raw-overwrite.yaml /global/u2/h/hungwei/legend-dataflow-new/inputs/dataprod/overrides/hit/muc/p03/r001/l200-p03-r001-muc-T%-par_hit-overwrite.yaml 
--hit-file /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/hit/phy/p03/r001/l200-p03-r001-phy-20230321T165925Z-tier_hit.lh5 
--tcm-file /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/tcm/phy/p03/r001/l200-p03-r001-phy-20230321T165925Z-tier_tcm.lh5 
--dsp-file /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/dsp/phy/p03/r001/l200-p03-r001-phy-20230321T165925Z-tier_dsp.lh5 
--output /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/evt/phy/p03/r001/l200-p03-r001-phy-20230321T165925Z-tier_evt.lh5 
--ann-file /global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/generated/tier/ann/phy/p03/r001/l200-p03-r001-phy-20230321T165925Z-tier_ann.lh5
```

### The `build-tier-evt` wrapper
The actual executable that is run in this step is `/global/cfs/cdirs/m2676/data/lngs/l200/public/prodenv/prod-blind/auto/v2.0.0/.snakemake/legend-dataflow/venv/bin/build-tier-evt`. The lines before it are the environment variables passed to the process, and the lines after it are the flags.

The script is actually just a wrapper that calls the function `build_tier_evt`:

```
# Executable "build-tier-evt"

#!/data2/public/prodenv/prod-blind/auto/v2.0.0/.snakemake/legend-dataflow/venv/bin/python

import sys
from legenddataflow.scripts.tier.evt import build_tier_evt
if __name__ == "__main__":
    if sys.argv[0].endswith("-script.pyw"):
        sys.argv[0] = sys.argv[0][:-11]
    elif sys.argv[0].endswith(".exe"):
        sys.argv[0] = sys.argv[0][:-4]
    sys.exit(build_tier_evt()) 
```

### Inside `build_tier_evt` (`evt.py`)
We then look for the function `build_tier_evt` in the script `evt.py` under `src` in this repository (`legend-dataflow`). It is pretty lengthy, so I will only give some remarks:

#### 1. Mapping args to the values of the flags
```
# Line 18 -36 of evt.py
def build_tier_evt() -> None:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--hit-file")
    argparser.add_argument("--dsp-file")
    argparser.add_argument("--tcm-file")
    argparser.add_argument("--ann-file", nargs="*")
    argparser.add_argument("--xtc-file", nargs="*")
    argparser.add_argument("--par-files", nargs="*")

    argparser.add_argument("--datatype", required=True)
    argparser.add_argument("--timestamp", required=True)
    argparser.add_argument("--tier", required=True)

    argparser.add_argument("--configs", required=True)
    argparser.add_argument("--metadata", required=True)
    argparser.add_argument("--log")

    argparser.add_argument("--output")
    args = argparser.parse_args()
```

We can see that the flags from earlier are used in this script. Whenever we see something like `args.datatype`, we can immediately look at our summarized dry-run output to find its value.

#### 2. The evt config defines which fields are produced in the LH5 file, and how
The script will read the general config file first:
```
# inputs/dataprod/config/l200-p03-r%-T%-all-config.yaml 
snakemake_rules: 
  # Other tiers are skipped
  tier_evt:
    inputs:
      evt_config:
        - $_/tier/evt/l200-p03-r%-T%-all-evt_config.yaml
        - $_/tier/evt/l200-p03-r%-T%-geds-evt_config.yaml
        - $_/tier/evt/l200-p03-r%-T%-geds_qc-evt_config.yaml
        - $_/tier/evt/l200-p03-r%-T%-geds_psd-evt_config.yaml
        - $_/tier/evt/l200-p03-r%-T%-spms-evt_config.yaml
      muon_config:
        evt_config: $_/tier/evt/l200-p03-r%-T%-muon-evt_config.yaml
        field_config: $_/tier/evt/l200-p03-r%-T%-muon-field_config.yaml
    options:
      logging: $_/log/basic_logging.yaml
      logger: prod
```
and then read the yaml files specified by the `evt_config` key:
```
# inputs/dataprod/config/tier/evt/l200-p03-r%-T%-all-evt_config.yaml
channels:
  pulser_aux: ch1027201
  muon_aux: ch1027202
  forced_aux: ch1027200

outputs:
  - trigger___timestamp
  - trigger___is_forced
  - coincident___puls
  - coincident___muon
  - coincident___geds
  - coincident___spms
  - coincident___spms_experimental
  - geds___rawid
  - geds___detector_name
  - geds___hit_idx
  - geds___multiplicity
  - geds___energy
  - geds___daqenergy
  - geds___energy_sum
  - geds___energy_no_xtc
  - geds___t0
  (skipped around 40 lines)

operations:
  trigger___timestamp:
    description: Timestamp of the event
    channels: pulser_aux
    aggregation_mode: sum
    expression: dsp.timestamp
    initial: 0
    lgdo_attrs:
      units: s

  _trigger___has_is_forced_aux_signal:
    description: >-
      True if a signal above threshold is found in the forced trigger auxiliary
      channel
    channels: forced_aux
    aggregation_mode: any
    expression: (dsp.wf_max - dsp.bl_mean) > 1000
    initial: false
(and a lot more blocks for operations of each field)
```

#### 3. The main call to `build_evt` in pygama
```
from pygama.evt import build_evt 
# (......100 lines ......)
# Line 104-117
    file_table = {
        "tcm": (args.tcm_file, "hardware_tcm_1", "ch{}"),
        "dsp": (args.dsp_file, "dsp", "ch{}"),
        "hit": (args.hit_file, "hit", "ch{}"),
        "evt": (None, "evt"),
    }

    if len(args.ann_file) > 0:
        file_table["ann"] = (args.ann_file[0], "dsp", "ch{}")

    table = build_evt(
        file_table,
        evt_config,
    )
```
The main purpose of this script is to read the configs and replace some of the placeholders inside them with the actual file names given by the values passed through the flags. After that, the config is passed to the main function `build_evt`, defined in pygama. That function returns a table, and this script writes the table to the LH5 file with `lh5.write()`.

#### 4. Some cross-talk specific notes
a. We can see that the flag `--xtc-file` is used, and an explicit path is given for it in the dry-run output. That file is definitely worth checking out.

b. In the evt config, the description of the operation `geds___energy` says that this field holds the corrected energy. The expression of the operation also shows the function used. I should check how the operations handle expressions, and what the function in the expression actually does to correct the energies with the cross-talk values.

## Breakdown of `build_evt` from pygama

`build_evt.py` (in `pygama/evt/`) is the module that transforms **per-channel, hit-structured data into per-event data**. In LEGEND, each detector channel is digitized and processed independently through the `dsp` and `hit` tiers, so a single physical event (a coincidence of several channels firing) is scattered across many channel tables. The `evt` tier stitches those back together into **one row per event**, with user-defined columns such as total multiplicity, summed energy, or "is this a muon".

### The central idea: the TCM

The glue that makes this possible is the **TCM (Time Coincidence Map)**, produced in an earlier tier. It is a flat list that records, for each event, *which channels participated and at which row in their channel table*. Almost everything in this module is fundamentally a **`groupby` driven by the TCM**: for each output event, use the TCM to gather the relevant rows from each channel's `hit`/`dsp` table, evaluate the user's expression on them, and combine the per-channel results.

### The call chain

The entry point called from `evt.py` (line 114) is `build_evt`, and the work flows downward:

```
evt.py:114  build_evt(file_table, evt_config)
   └─ build_evt(...)              # config validation + channel-list resolution
        └─ build_evt_cols(...)    # chunked TCM loop; builds each evt column
             └─ evaluate_expression(...)      # dispatch on aggregation_mode
                  └─ aggregators.evaluate_to_*(...)   # the actual TCM groupby
                       └─ utils.get_data_at_channel(...)  # read rows + eval() the expression
```

The recurring engine underneath everything is the **TCM-driven groupby plus Python `eval()` on string expressions**, which is what lets the YAML config express arbitrary per-event physics without any code changes.

### Background: `Table`, "field", and "attribute"

Before the functions, three LGDO concepts that the module relies on:

- **`Table`** — an LGDO (LEGEND Data Object) container, "a special struct of arrays or subtable columns of equal length". It is the in-memory twin of an HDF5 **group** on disk. It holds named **columns**, all with the same number of rows (one row = one event). Each column is itself an LGDO object — an `Array` (1D column), `VectorOfVectors` (jagged column), `ArrayOfEqualSizedArrays`, or even a nested `Table` (this is how `coincident/muon` becomes a sub-group). Note that `len(table)` returns the number of **fields (columns)**, not rows; the row count is the `size` attribute, set via `Table(size=...)`.
- **"field"** — the LGDO name for a **column**. Hence `add_field`, `keys()`, `items()`. On disk each field is an HDF5 dataset inside the group. Field / column / dataset all mean the same thing at different layers.
- **"attribute"** — a small piece of **HDF5 metadata attached to a dataset or group**, stored *alongside* the data. Every LGDO exposes them as a `.attrs` dict. The mandatory one is `datatype` (e.g. `"array<1>{real}"`, `"table{...}"`), which tells LGDO how to interpret the raw bytes; others include `units`, `bit_names` (labels for the bits of a quality-flags field), and `description`.

**Accessing a column from an in-memory Table** (once you already have the object, `read()` is not needed — that was only the disk→memory step):

```python
tbl = build_evt(file_table, evt_config)   # in-memory Table (evt.file is None)

col = tbl["energy"]              # -> an LGDO column (Array / VectorOfVectors), NOT a raw array
sub = tbl["coincident/muon"]     # bracket access also supports nested paths

energies = tbl["energy"].view_as("np")   # numpy array, one value per event
tbl["energy"].view_as("ak")              # awkward array (works for jagged columns too)
tbl["energy"].view_as("pd")              # pandas Series
tbl["energy"].nda                        # raw numpy ndarray (Array columns only)

tbl.view_as("pd")                # whole table -> pandas DataFrame (== tbl.get_dataframe())
print(tbl["energy"].attrs)       # {'datatype': ..., 'units': 'keV', ...}
```

Attribute-style access (`tbl.energy`) also works, but prefer `tbl["energy"]`: real methods/attributes like `tbl.size`, `tbl.loc`, `tbl.keys` would shadow a field of the same name, whereas bracket access has no such ambiguity.

### `channels` vs `channel_mapping`

Two config-derived structures that are easy to conflate — **neither holds rich metadata**, both are reduced to plain strings by the time they reach `build_evt`:

| | `channels` | `channel_mapping` |
|---|---|---|
| Shape | `group_name -> [ids]` (nested) | `id -> name` (flat, 1-to-1) |
| Contains | channel-ID strings only | detector-name strings only |
| Purpose | **select** which channels an operation runs over | **label** a channel ID with its name inside functions |

- **`channels`** is a dict of named *groups*, each mapping to a list of channel-ID strings, e.g. `{"geds_on": ["ch1084803", ...], "muon_aux": ["ch1027202"]}`. When an operation says `"channels": "muon_aux"`, that names a group, which `build_evt_cols` expands to the concrete channel list to loop over.
- **`channel_mapping`** is a flat lookup `{"ch1084803": "Gethin", ...}`. In `evt.py` it is built from `chmap` but only `dic.name` is kept — so it carries no other metadata. It is threaded down and, in `function` mode, injected into the function namespace so a custom module function can use a detector *name* instead of the raw `ch...` ID. The plain aggregators mostly ignore it.

The richer metadata lives in the `chmap` object back in `evt.py`, from which `channel_mapping` is derived by pulling out only `.name`.

### `build_evt` — the configuration front-end

Purpose: public entry point; it validates and prepares but does not touch data itself.

- Loads the config (dict or file) and asserts the mandatory `channels` and `operations` blocks exist.
- Normalizes `datainfo` into a `DataInfo` named tuple mapping each tier name → `(file, group, table_fmt)`. In the call from `evt.py`, `evt` has `file=None`, which is the signal to **return the table in memory** rather than write it to disk.
- Validates the channel-name format string (`ch{}`) has exactly one placeholder and actually matches keys in the hit file.
- **Resolves the channel dictionary**: each entry in `config["channels"]` becomes a concrete list of channel names. A value can be a plain string, a list, or a `dict` naming a metadata `module` to import and call dynamically. (In `evt.py` the lists are already filled in from the channel map *before* `build_evt` is called, so here they arrive as plain lists.)
- Delegates all real work to `build_evt_cols` and returns its result (or `None` if writing to a file).

### `build_evt_cols` — the driver loop

Purpose: iterate over the TCM in chunks, build every requested output column, arrange them into (possibly nested) tables, and either write or return them.

**1. Attribute pre-computation (once, before the loop).** For any operation whose expression references *exactly one* lower-tier field (e.g. `hit.quality_flags`), it reads that field's LGDO **attributes** (like `bit_names`) once and stashes them, to be copied onto the output column later.

Two things to be precise about here:
- This block pre-computes **attributes (metadata) only — never column data**. The actual numbers in every column are always produced inside the TCM loop, regardless of aggregation mode. "Attribute forwarding" and "evaluating the expression" are two independent activities that happen to concern the same operation.
- `get_lgdo_attrs` reads the attrs from the **first channel whose table contains that field**. This is correct because an attribute like `bit_names` describes the *meaning* of the field (a schema label identical across all channels), not per-channel data — so any one channel's copy will do. It is a metadata-only `h5py` read; **no array data is loaded**, which is why it is cheap enough to do once up front. `function` mode and multi-field expressions are excluded, since their output has no single source field whose attrs would remain meaningful.

**2. Chunked TCM iteration.** Uses an `LH5Iterator` over the TCM with `buffer_len` rows at a time (default 10⁴), reading only `table_key` (which channel) and `row_in_table` (which row) as awkward arrays.

A subtlety about `Table(size=len(tcm_lh5))`: the loop variable `tcm_lh5` is **not** the iterator — it is the *buffer* the iterator yields each step, and `len(tcm_lh5)` is the number of rows **in the current chunk**. That equals `buffer_len` for every *full* chunk but is smaller for the **last** chunk (the remainder), because `read` resizes the buffer to `min(buffer_len, rows_remaining)`. This is exactly why the code sizes the per-chunk table with `len(tcm_lh5)` rather than the constant `buffer_len` — hardcoding `buffer_len` would over-size the final chunk's table and pad it with garbage rows. (Do not confuse this with `len(the_iterator)` itself, which returns the *total* number of entries in the whole dataset.) The in-source comment "get number of events in file" is therefore loosely worded — it is the number of events in *this chunk*, not the file.

**3. Per-operation loop.** Dictionary order matters — a column computed early can be referenced (as `evt.<name>`) by a later one. Each operation takes one of two branches:
- **No `aggregation_mode`** → a pure evt-level expression, evaluated directly with `table.eval()` on already-built columns.
- **Has `aggregation_mode`** → resolves the channel include/exclude lists, parses the `initial`/default value, and calls `evaluate_expression`. Afterwards it attaches attributes (forwarded source attrs, then user `lgdo_attrs` which override, then `description`), optionally casts to `dtype`, and adds the column to the table.

**4. Output shaping.** Keeps only fields listed in `outputs`, and turns `___`-separated names into nested sub-tables (`coincident___muon` → `coincident/muon`).

**5. Combining the per-chunk tables.** How chunks are merged depends on the output mode:
- **Writing to disk** (`evt.file` is a real path): each chunk's shaped table is appended straight to the output LH5 file with `lh5.write(..., wo_mode="a")`; nothing is kept in memory, and there is no final concatenation. This is the memory-efficient path that chunking is designed for.
- **In-memory** (`evt.file is None`, the path `evt.py` uses): each chunk's table is collected into a Python list and merged after the loop by `_concat_tables`, which does a **row-wise (axis=0) concatenation** via awkward: convert each chunk `Table` to an awkward array, `ak.concatenate(..., axis=0)` to stack the rows, wrap back into one `Table`, and `readd_attrs` to re-apply the LGDO attributes (the awkward round-trip drops them). The result is a single `Table` holding all events across all chunks — this is what is returned to `evt.py` line 114.

  Consequence worth noting: in this in-memory path every chunk table is held in the list until the end, so the whole output sits in RAM regardless — chunking there only bounds the *read* buffer, not total memory. Only the disk-writing path truly keeps peak memory low.

### `evaluate_expression` — dispatch on aggregation mode

Purpose: compute a *single* column by evaluating one user expression across a set of channels and combining the per-channel results according to `mode`. This function decides *which* strategy runs and delegates the heavy lifting to `aggregators`.

- **Builds the parameter namespace**: existing evt columns (`Array`/`VectorOfVectors`) plus explicit `parameters` from the config become variables usable in the expression.
- **`function` mode** is the general escape hatch: the expression is a *function call* (e.g. `pygama.evt.modules.spms.gather_pulse_data(...)`). It regex-parses the argument list, dynamically imports the module, injects the mandatory args (`datainfo, tcm, table_names, channel_mapping`), and runs the whole thing through `eval()`.
- **Field discovery**: a regex finds all `tier.field` tokens (e.g. `hit.cuspEmax_ctc_cal`) so downstream code knows what to read from disk.
- **Query handling**: an optional masking expression; mixing `evt.`-tier and lower-tier references is forbidden, and an evt-level query is pre-evaluated directly.
- **Mode dispatch** — each maps to an aggregator:
  - `keep_at_ch:` / `keep_at_idx:` → `evaluate_at_channel[_vov]`: pick the value from a channel chosen per-event by another column (e.g. energy of the highest-energy detector).
  - `first_at:` / `last_at:` → `evaluate_to_first_or_last`: pick the value from the channel with the min/max of a sorter field.
  - `sum` / `any` / `all` → `evaluate_to_scalar`: reduce across channels.
  - `gather` → `evaluate_to_vector`: do not combine — keep all channels' values as a `VectorOfVectors` per event.

### The aggregators and `get_data_at_channel` — the actual work

The aggregators all share the same skeleton: **loop over channels**, and for each, use the TCM to find that channel's rows.

- For a channel `ch`, `table_id = get_tcm_id_by_pattern(...)`, then `chan_tcm_indexs = ak.flatten(tcm.table_key) == table_id` selects the TCM entries belonging to this channel, and `idx_ch = row_in_table[chan_tcm_indexs]` gives the exact rows to read from that channel's own `hit`/`dsp` table. This is the groupby key.
- **`get_data_at_channel`** is where the expression is actually computed. It special-cases the TCM pseudo-fields (`tcm.table_key`, `tcm.row_in_table`, `tcm.index`); otherwise it reads the needed fields for `idx_ch`, rewrites tier prefixes into valid Python identifiers (`hit.cuspEmax_ctc_cal` → `hit_cuspEmax_ctc_cal`, `evt.foo` → `foo`), and runs `eval(new_expr, var)`. The result must reduce to a 1D array per channel.
- Each aggregator then scatters those per-channel results into the `n_rows`-length output using the event indices, combining per its mode (min/max sort, sum/or/and, pick-at-channel, or gather into a jagged vector), applying the optional query mask along the way.

### Worked example: `coincident___muon`

```yaml
coincident___muon:
  description: >-
    True if this is flagged as a muon event. Determined by looking for a
    signal in the muon veto auxiliary channel
  channels: muon_aux
  aggregation_mode: any
  expression: dsp.wf_max > 15100
  initial: false
```

This operation **does** go through the full TCM loop — that is the only place its boolean values are produced. The pre-computation block touches it only to notice `dsp.wf_max` is a single referenced field and stash its (probably trivial) attrs. Assuming `muon_aux` resolves to `["ch1027202"]`:

1. In `build_evt_cols` (inside the chunk loop) the op has an `aggregation_mode`, so it takes the aggregation branch: `channels_e = ["ch1027202"]`, `channels_skip = []`, `defaultv = False` (from `initial`). It calls `evaluate_expression(mode="any", expr="dsp.wf_max > 15100", channels=["ch1027202"], default_value=False, n_rows=<events in chunk>)`.
2. In `evaluate_expression`: `field_list = [("dsp", "wf_max")]`; `mode == "any"` dispatches to `aggregators.evaluate_to_scalar`.
3. In `evaluate_to_scalar`, for the single channel `ch1027202`:
   - **Find its TCM entries**: `table_id = 1027202`; `chan_tcm_indexs = ak.flatten(tcm.table_key) == 1027202`; `idx_ch = ak.flatten(tcm.row_in_table)[chan_tcm_indexs]` — the rows of the muon channel's `dsp` table to read.
   - **Read + evaluate**: `get_data_at_channel` reads `ch1027202/dsp/wf_max` at `idx_ch`, rewrites the expression to `dsp_wf_max > 15100`, and `eval`s it → a boolean array, one entry **per muon hit** (not per event).
   - **Prepare output**: `out = make_numpy_full(n_rows, False, bool)` — one entry **per event**, initialized to the `initial: false`.
   - **Map hits back to events**: `evt_ids_ch = np.repeat(np.arange(n_events), ak.sum(tcm.table_key == table_id, axis=1))` gives, for each muon hit, the event index it belongs to.
   - **Scatter-reduce with `any`**: `out[evt_ids_ch] |= res & limarr` (here `limarr` is all-True, no query). Events where the muon channel never fired are never indexed, so they keep the initial `False` — this is exactly why `initial: false` is specified.
4. Back in `build_evt_cols`: the resulting `Array` gets any forwarded attrs + the `description`, and the `___` in the name routes it into a nested sub-table, so `coincident___muon` becomes `coincident/muon` in the output.

**Result**: for each event, `coincident/muon` is `True` iff the muon-veto aux channel participated in that event *and* its `wf_max` exceeded 15100.
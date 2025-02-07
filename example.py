"""Example code for manual SIP creation."""
from mets_builder import (
    METS,
    MetsProfile,
    StructuralMap,
    StructuralMapDiv,
)
from mets_builder.metadata import (
    DigitalProvenanceEventMetadata,
    ImportedMetadata,
)

from siptools_ng.file import File
from siptools_ng.sip import SIP

# A part of using dpres-siptools-ng is to create a METS object using
# dpres-mets-builder in tandem with some helper utilities provided by
# dpres-siptools-ng whenever needed. See user documentation of
# dpres-mets-builder at
# https://github.com/Digital-Preservation-Finland/dpres-mets-builder for more
# detailed instructions on how to build METS objects. This example code focuses
# on automating the METS creation as much as possible.

# Initialize dpres-mets-builder METS object with your information
mets = METS(
    mets_profile=MetsProfile.CULTURAL_HERITAGE,
    contract_id="urn:uuid:abcd1234-abcd-1234-5678-abcd1234abcd",
    creator_name="CSC – IT Center for Science Ltd.",
    creator_type="ORGANIZATION"
)

# Create files each containing a digital object which contains the sip path.
file1 = File(
    path="static/DATA/Testivideo-FFV1-FLAC.mkv",
    digital_object_path="DATA/Testivideo-FFV1-FLAC.mkv"
)
file2 = File(
    path="static/DATA/Testikuva-JPEG.jpeg",
    digital_object_path="DATA/Testikuva-JPEG.jpeg"
)
file3 = File(
    path="static/DATA/Testikuva-TIFF-fixed.tif",
    digital_object_path="DATA/Testikuva-TIFF-fixed.tif"
)

# Create provenance metadata
provenance_md = DigitalProvenanceEventMetadata(
    event_type="creation",
    detail="This is a detail",
    outcome="success",
    outcome_detail="Another detail",
)

# Import descriptive metadata from an XML source
descriptive_md = ImportedMetadata.from_path("static/METADATA/lido_description.xml")

# Add metadata to files
file1.add_metadata([provenance_md])
file2.add_metadata([provenance_md, descriptive_md])
file3.add_metadata([descriptive_md])

###################################
# Try to link Apple ProRes video to sip
###################################
source_file = File(
    path="static/DATANATIVE/Jussila_Yojuna_ProRes_PCMx2.mov",
    digital_object_path="DATANATIVE/Jussila_Yojuna_ProRes_PCMx2.mov"
)

outcome_file = File(
    path="static/DATA/Jussila_Yojuna_FFV1_FLACx2.mkv",
    digital_object_path="DATA/Jussila_Yojuna_FFV1_FLACx2.mkv"
)

source_file.digital_object.use = "fi-dpres-no-file-format-validation"
source_file.generate_technical_metadata()
outcome_file.generate_technical_metadata()

event = mets_builder.metadata.DigitalProvenanceEventMetadata(
    event_type = "migration",
    detail = "Normalization of digital object.",
    outcome = "success",
    outcome_detail = ("Source file format has been normalized. Outcome "
                      "object has been created as a result."),
    datetime = "2024-08-14T15:22:00",
)

source_file_techmd = next(
    metadata for metadata in source_file.metadata
    if metadata.metadata_type.value == "technical"
    and metadata.metadata_format.value == "PREMIS:OBJECT"
)
event.link_object_metadata(
    source_file_techmd,
    object_role="source"
)
outcome_file_techmd = next(
    metadata for metadata in outcome_file.metadata
    if metadata.metadata_type.value == "technical"
    and metadata.metadata_format.value == "PREMIS:OBJECT"
)
event.link_object_metadata(
    outcome_file_techmd,
    object_role="outcome"
)
source_file.add_metadata([event])
outcome_file.add_metadata([event])
###################################

'''''''''
# Make a custom structural map div using the digital objects in files
root_div = StructuralMapDiv(
    "custom_div",
    digital_objects=[
        file1.digital_object,
        file2.digital_object,
        file3.digital_object
    ],
)

# Add the custom div to a structural map
structural_map = StructuralMap(root_div=root_div)

# Add the custom structural map to METS and generate file references
mets.add_structural_maps([structural_map])
mets.generate_file_references()
'''''''''
# Make a SIP using the previously created file and METS. In addition to the
# manually structural map a default custom map is generated based on the
# directory structure.
sip = SIP.from_files(mets=mets, files=[file1, file2, file3, source_file, outcome_file])

# Finalize the SIP and write it to file
sip.finalize(
    output_filepath="static/SIP/example-manual-sip.tar",
    sign_key_filepath="signature/sip_sign_pas.pem"
)
sip.mets.write("static/SIP/mets.xml")
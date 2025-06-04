# construction.cc

concc = """
#include "construction.hh"

MyDetectorConstruction::MyDetectorConstruction()
{
	fMessenger = new G4GenericMessenger(this, "/detector/", "Detector Construction");

	fMessenger -> DeclareProperty("nCols", nCols, "Number of columns");
	fMessenger -> DeclareProperty("nRows", nRows, "Number of rows");

	nCols = 50;
	nRows = 50;

	DefineMaterials();
}

MyDetectorConstruction::~MyDetectorConstruction()
{}

void MyDetectorConstruction::DefineMaterials()
{
	G4NistManager *nist = G4NistManager::Instance();

    worldMat = nist -> FindOrBuildMaterial("%s");

%s
}

G4VPhysicalVolume *MyDetectorConstruction::Construct()
{
    G4double xWorld = %s;
    G4double yWorld = %s;
    G4double zWorld = %s;
    G4double xDet   = %s;
    G4double yDet   = %s;
    G4double zDet   = %s;
    G4double zPVPd  = %s;
	G4double zPMT   = 10.*mm;
	G4bool checkOverlaps = true;

	solidWorld = new G4Box("solidWorld", xWorld/2, yWorld/2, zWorld/2);
	logicWorld = new G4LogicalVolume(solidWorld, worldMat, "logicWorld");
	phys_World = new G4PVPlacement(0, G4ThreeVector(0., 0., 0.), logicWorld, "phys_World", 0, false, 0, checkOverlaps);

	solidDetector = new G4Box("solidDetector", xDet/2, yDet/2, zDet/2);
    logicDetector = new G4LogicalVolume(solidDetector, %s, "logicDetector");
    phys_Detector = new G4PVPlacement(0, G4ThreeVector(0., 0., zPVPd), logicDetector, "phys_Detector", logicWorld, false, 0, checkOverlaps);

%s

	fScoringVolume = logicDetector;

	return phys_World;
}

void MyDetectorConstruction::ConstructSDandField()
{
	MySensitiveDetector *sensDet = new MySensitiveDetector("SensitiveDetector");

	%s -> SetSensitiveDetector(sensDet);
}
"""



# construction.hh
conhh = """
#ifndef CONSTRUCTION_HH
#define CONSTRUCTION_HH

#include "G4VUserDetectorConstruction.hh"
#include "G4VPhysicalVolume.hh"
#include "G4LogicalVolume.hh"
#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4PVPlacement.hh"
#include "G4NistManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4GenericMessenger.hh"

#include "detector.hh"

class MyDetectorConstruction : public G4VUserDetectorConstruction
{
public:
	MyDetectorConstruction();
	~MyDetectorConstruction();

	G4LogicalVolume *GetScoringVolume() const
	{
		return fScoringVolume;
	}

	virtual G4VPhysicalVolume *Construct();

private:
	virtual void ConstructSDandField();

	G4int nCols, nRows;

	G4Box             *solidWorld, *solidDetector, *solidPMT;
	G4VPhysicalVolume *phys_World, *phys_Detector, *phys_PMT;
	G4LogicalVolume   *logicWorld, *logicDetector, *logicPMT, *fScoringVolume;

	G4GenericMessenger *fMessenger;
	G4Material *worldMat, %s;

	void DefineMaterials();
};

#endif
"""



# generator.cc
gencc = """
#include "generator.hh"

MyPrimaryGenerator::MyPrimaryGenerator()
{
    fParticleGun = new G4ParticleGun(1);

    G4ParticleTable *particleTable = G4ParticleTable::GetParticleTable();
    G4ParticleDefinition *particle = particleTable -> FindParticle("%s");

    G4ThreeVector pos(0.,0.,0.);
    G4ThreeVector mom(0.,0.,1.);

    fParticleGun -> SetParticlePosition(pos);
    fParticleGun -> SetParticleMomentumDirection(mom);
    fParticleGun -> SetParticle%s;
    fParticleGun -> SetParticleDefinition(particle);
}

MyPrimaryGenerator::~MyPrimaryGenerator()
{
    delete fParticleGun;
}

void MyPrimaryGenerator::GeneratePrimaries(G4Event *anEvent)
{
    fParticleGun -> GeneratePrimaryVertex(anEvent); 
}
"""



# pmt
pmt = """
	solidPMT = new G4Box("solidPMT", xWorld/nRows, yWorld/nCols, zPMT);
	logicPMT = new G4LogicalVolume(solidPMT, worldMat, "logicPMT");

	for (G4int i = 0; i < nRows; i++)
	{
		for (G4int j = 0; j < nCols; j++)
		{
			phys_PMT = new G4PVPlacement(0, G4ThreeVector((-xWorld + (i+0.5)*(xWorld*2./nRows))*mm, (-yWorld + (j+0.5)*(yWorld*2./nCols))*mm, zWorld-zPMT),
												logicPMT, "phys_PMT", logicWorld, false, i * nRows + j, checkOverlaps);
		}
	}
"""
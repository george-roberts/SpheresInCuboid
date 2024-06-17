import adsk.core, adsk.fusion, adsk.cam, traceback, math, random

def generate_spheres_in_cuboid(cuboid_width, cuboid_height, cuboid_depth, max_spheres):
    # Helper function to check if two spheres overlap
    def does_overlap(sphere1, sphere2):
        distance = math.sqrt((sphere1[0] - sphere2[0])**2 + (sphere1[1] - sphere2[1])**2 + (sphere1[2] - sphere2[2])**2)
        return distance < (sphere1[3] + sphere2[3])
    
    # Helper function to check if a sphere is inside the cuboid
    def is_inside_cuboid(x, y, z, r):
        return (r <= x <= cuboid_width - r) and (r <= y <= cuboid_height - r) and (r <= z <= cuboid_depth - r)
    
    spheres = []
    grid_size = min(cuboid_width, cuboid_height, cuboid_depth) / 10  # Adjust grid size for better packing
    for _ in range(max_spheres):
        for attempt in range(200):  # Increase attempts to find better positions
            radius = random.uniform(grid_size / 2, grid_size)  # Larger radius range for tighter packing
            x = random.uniform(radius, cuboid_width - radius)
            y = random.uniform(radius, cuboid_height - radius)
            z = random.uniform(radius, cuboid_depth - radius)
            new_sphere = (x, y, z, radius)
            
            if all(not does_overlap(new_sphere, existing_sphere) for existing_sphere in spheres) and is_inside_cuboid(x, y, z, radius):
                spheres.append(new_sphere)
                break

    return spheres

def create_spheres_in_fusion(spheres, app, ui, design):
    root_comp = design.rootComponent
    temp_brep_mgr = adsk.fusion.TemporaryBRepManager.get()
    
    # Create a base feature
    base_feature = root_comp.features.baseFeatures.add()
    base_feature.startEdit()

    for sphere in spheres:
        center = adsk.core.Point3D.create(sphere[0], sphere[1], sphere[2])
        radius = sphere[3]
        
        # Create a temporary sphere
        temp_sphere = temp_brep_mgr.createSphere(center, radius)
        
        # Add the sphere to the root component
        body = root_comp.bRepBodies.add(temp_sphere, base_feature)
    
    # Finish the base feature edit
    base_feature.finishEdit()

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        doc = app.activeDocument
        prods = doc.products
        design = adsk.fusion.Design.cast(prods.itemByProductType("DesignProductType"))
        
        if not design:
            ui.messageBox('No active Fusion design', 'Error')
            return

        # Define cuboid dimensions and number of spheres
        cuboid_width = 100
        cuboid_height = 50
        cuboid_depth = 30
        max_spheres = 100
        
        # Generate spheres
        spheres = generate_spheres_in_cuboid(cuboid_width, cuboid_height, cuboid_depth, max_spheres)
        
        # Create the spheres in Fusion 360
        create_spheres_in_fusion(spheres, app, ui, design)
        
    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

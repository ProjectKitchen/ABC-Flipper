
$fs = 0.01;

difference() {

  difference() {
    color("red", alpha=0.5)
          translate ([-0, -0, 0])
            resize(newsize=[14,10,4]) sphere(r=1);

    translate ([0,0,-5.5])
         resize ([15, 15, 10])  cube(1, center=true);

//    color("green", alpha=0.5)
//          translate ([-0, 0, -1])
//            resize(newsize=[13,9,3]) sphere(r=1);
    }


    union() {
        translate ([-0, -0, -0.5])
          linear_extrude(4) 
            circle(3);
        translate ([-4, -3, 0])
            cylinder(h=5,r=0.5, center=true);
        translate ([4, -3, 0])
            cylinder(h=5,r=0.5, center=true);
        translate ([-4, 3, 0])
            cylinder(h=5,r=0.5, center=true);
        translate ([4, 3, 0])
            cylinder(h=5,r=0.5, center=true);

        translate ([0,0,-1])
            resize ([9, 7, 3])  cube(1, center=true);

    }
}



/*

color("green")
    translate([0, 30, 0])
        rotate_extrude($fn = 80)
            polygon( points=[[0,0],[8,4],[4,8],[4,12],[12,16],[0,20]] );
            
            
color("red")
    translate([10, -10, 0])
        linear_extrude(10)
            polygon( points=[[0,0],[8,4],[4,8],[4,12],[12,16],[0,20]] );
*/
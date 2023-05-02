
$fs = 0.01;

difference() {

    intersection() {
        linear_extrude(1) 
            resize([15,12]) circle(1);
            square ([12,9],true);
    }

    union() {
        translate ([-0, -0, -0.5])
          linear_extrude(2) 
            circle(3);
        translate ([-4, -3, 0])
            cylinder(h=2,r=0.5, center=true);
        translate ([4, -3, 0])
            cylinder(h=2,r=0.5, center=true);
        translate ([-4, 3, 0])
            cylinder(h=2,r=0.5, center=true);
        translate ([4, 3, 0])
            cylinder(h=2,r=0.5, center=true);
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
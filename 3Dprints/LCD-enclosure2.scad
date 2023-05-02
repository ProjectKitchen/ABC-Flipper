
$fs = 0.01;



l=54;
w=45;
h=30;
add_l=33;
add_w=27;
letterHole=13;


difference() {

  difference() {
    color("red")
          translate ([-0, -0, 0])
            resize(newsize=[l+add_l,w+add_w,h]) sphere(r=1);

    union() {
      translate ([0,0,8])
         resize ([l, w, h])  cube(1, center=true);

      translate ([0,-83,0]) rotate ([-10,0,0])
         resize ([100, 100, 100])  cube(1, center=true);

      translate ([0,0,-37]) 
         resize ([100, 100, 50])  cube(1, center=true);
      }
    }


    union() {
        translate ([-0, -0, -50])
          linear_extrude(100) 
            circle(letterHole);
/*
        translate ([-4, -3, 0])
            cylinder(h=5,r=0.5, center=true);
        translate ([4, -3, 0])
            cylinder(h=5,r=0.5, center=true);
        translate ([-4, 3, 0])
            cylinder(h=5,r=0.5, center=true);
        translate ([4, 3, 0])
            cylinder(h=5,r=0.5, center=true);
*/
        translate ([0,0,-100])
            resize ([l, w, h])  cube(1, center=true);

    }
}


translate ([0,-28,0]) rotate([80,0,0])resize ([40,15,10]) cylinder(1,1,1);


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
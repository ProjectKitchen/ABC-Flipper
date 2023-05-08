
$fs = 0.01;
$fn = 80;

l=54;
w=46;
h=22;
edge=2;
letterHole=13;
thickness=3.5;


module front() {
    difference() {
        linear_extrude(h)  square ([l+thickness,w+thickness],true);
        union() {
            translate ([-0, -0, -0.5])
              linear_extrude(l+1) {
                translate ([0, -0, -0]) circle(letterHole);
                translate ([l/2-edge+2,w/2-edge+2,0])
                    difference() {square(edge+2);circle(edge);}
                translate ([-(l/2-edge+2),(w/2-edge+2),0])
                    rotate(90) difference() {square(edge+1);circle(edge);}
                translate ([-(l/2-edge+2),-(w/2-edge+2),0])
                    rotate(180) difference() {square(edge+1);circle(edge);}
                translate ([(l/2-edge+2),-(w/2-edge+2),0])
                    rotate(270) difference() {square(edge+1);circle(edge);}
            }
        }
    }
}


module stand() {
 rotate([2,0,0]) 
 difference() {
    color("red")   rotate([90,0,0]) linear_extrude(20) scale([2,2,1]) circle(d=9);
 }
}

difference() {
  union() {
    // box
    difference() {
        front();
        translate ([0,0,-3])
           linear_extrude(h)  square ([l,w],true);
    }

    // stand
     translate ([0,-24,10]) stand();
   }
  union() {
   translate ([0,-20,9]) rotate([90,0,0]) cylinder(50,6,6);
   translate ([17,-20,9]) rotate([90,0,0]) cylinder(50,2.1,2.1);
   translate ([-17,-20,9]) rotate([90,0,0]) cylinder(50,2.1,2.1);
  }
}


color("blue")
 translate ([0,-80,0]) linear_extrude(2)  square ([l+thickness,w+thickness],true);

 translate ([0,-80 -w/2 +1.5,2]) linear_extrude(4)  square ([l-1,3],true);
 translate ([0,-80 +w/2 -1.5,2]) linear_extrude(4)  square ([l-1,3],true);


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
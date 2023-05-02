
$fs = 0.01;

l=54;
w=45;
h=20;
edge=2;
letterHole=13;



module front() {
    difference() {
        linear_extrude(h)  square ([l+2,w+2],true);
        union() {
            translate ([-0, -0, -0.5])
              linear_extrude(l+1) {
                translate ([-1, -0, -0]) circle(letterHole);
                translate ([l/2-edge+1,w/2-edge+1,0])
                    difference() {square(edge+1);circle(edge);}
                translate ([-(l/2-edge+1),(w/2-edge+1),0])
                    rotate(90) difference() {square(edge+1);circle(edge);}
                translate ([-(l/2-edge+1),-(w/2-edge+1),0])
                    rotate(180) difference() {square(edge+1);circle(edge);}
                translate ([(l/2-edge+1),-(w/2-edge+1),0])
                    rotate(270) difference() {square(edge+1);circle(edge);}
            }
        }
    }
}


module stand() {
 rotate([2,0,0]) 
 difference() {
    color("red")   rotate([90,0,0]) linear_extrude(20,true, 8, true, 2, 1) scale([2,1,1]) circle(d=10);
 }
}

difference() {
  union() {
    // box
    difference() {
        front();
        translate ([0,0,-2])
           linear_extrude(h)  square ([l,w],true);
    }

    // stand
     translate ([0,-22.6,7]) stand();
   }
   translate ([0,-10,7]) rotate([90,0,0]) cylinder(50,5,5);
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
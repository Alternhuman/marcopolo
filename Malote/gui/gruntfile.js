module.exports = function(grunt) {

   function bowerCopy(src_dir, src, dest) {
      return {
         expand: true,
         nonull: true,
         cwd: '<%= bowerdir %>/' + src_dir,
         src: src,
         dest: '<%= distdir %>/' + dest
      };
   }

   grunt.initConfig({
      pkg: grunt.file.readJSON('package.json'),
      distdir: 'dist',
      bowerdir: 'bower_components',
      src: {
         js: ['src/**/*.js'],
         partials: ['src/partials/**/*.part.html'],
         tests: ['src/tests/**/*.spec.js'],
         css: ['src/css/**/*.css'],
      },
      jshint: {
         files: ['gruntfile.js', '<%= src.js %>'],
         options: {
            "-W083": true, // functions within a loop
         },
      },
      uglify: {
         options: {
            banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
            sourceMap: true,
         },
         build: {
            src: 'src/**/*.js',
            dest: '<%= distdir %>/js/<%= pkg.name %>.min.js',
         }
      },
      concat_sourcemap: {
         options: {},
         build: {
            files: {
               '<%= distdir %>/js/<%= pkg.name %>.js': [
                  '<%= src.js %>',
                  '!<%= src.tests %>',
               ],
            },
         },
      },
      cssFiles: {
         '<%= distdir %>/css/<%= pkg.name %>.min.css': '<%= src.css %>',
      },
      symlink: {
            options: {
               overwrite: false,
            },
            css: {
               dest: 'dist/css/stylesheet.css',
               src: 'src/css/stylesheet.css',
            },
      },
      clean: ['<%= distdir %>/*'],
      recess: {
         min: {
            files: '<%= cssFiles %>',
            options: {
               compile: true,
               compress: true,
            },
         },
      },
      copy: {
         assets: {
            files: [
               {
                  expand: true,
                  cwd: 'src/assets',
                  src: ['**'],
                  dest: '<%= distdir %>/',
               },
            ],
         },
         partials: {
            files: [
               {
                  expand: true,
                  cwd: 'src/partials',
                  src: ['**/*.part.html'],
                  dest: '<%= distdir %>/partials',
               },
            ],
         },
         libraries: {
            files: [
               bowerCopy('angular', 'angular.js', 'js/'),
               bowerCopy('angular-animate', 'angular-animate.js', 'js/'),
               bowerCopy('angular-cookies', 'angular-cookies.js', 'js/'),
               bowerCopy('animate.css', 'animate.css', 'css/'),
               bowerCopy('lodash/dist', 'lodash.compat.js', 'js/'),
               bowerCopy('bootstrap/dist/js', 'bootstrap.js', 'js/'),
               bowerCopy('bootstrap/dist/css', 'bootstrap.css', 'css/'),
               bowerCopy('bootstrap/dist/fonts', 'glyphicons-halflings-regular.*', 'fonts/'),
               bowerCopy('font-awesome/css', 'font-awesome.css', 'css/'),
               bowerCopy('font-awesome/fonts', 'fontawesome-webfont.*', 'fonts/'),
            ],
         },
      },
      concat: {
         dist: {
            src: 'src/index.html',
            dest: '<%= distdir %>/index.html',
            options: {
               process: true,
            },
         },
      },
      watch: {
         files: [
            'gruntfile.js',
            'src/**/*.js',
            'src/**/*.html',
         ],
         tasks: ['debug', 'karma:unit:run'],
         options: {
            livereload: true,
         },
      },
      karma: {
         unit: {
            configFile: 'karma.conf.js',
            background: true,
            singleRun: false,
         },
      },
   });

   grunt.loadNpmTasks('grunt-contrib-uglify');
   grunt.loadNpmTasks('grunt-contrib-jshint');
   grunt.loadNpmTasks('grunt-contrib-clean');
   grunt.loadNpmTasks('grunt-contrib-copy');
   grunt.loadNpmTasks('grunt-contrib-concat');
   grunt.loadNpmTasks('grunt-contrib-jasmine');
   grunt.loadNpmTasks('grunt-recess');
   grunt.loadNpmTasks('grunt-concat-sourcemap');
   grunt.loadNpmTasks('grunt-contrib-watch');
   grunt.loadNpmTasks('grunt-contrib-symlink');
   grunt.loadNpmTasks('grunt-karma');

   // Default task(s)
   grunt.registerTask('default', ['debug']);
   grunt.registerTask('build', ['clean', 'jshint', 'karma:unit', 'copy:assets', 'concat']);
   grunt.registerTask('debug', ['build', 'copy:partials', 'copy:libraries', 'concat_sourcemap', 'symlink:css']);
   grunt.registerTask('release', ['build', 'uglify', 'recess:build']);
};
